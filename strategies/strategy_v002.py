# strategy_v002.py
import logging
import numpy as np
import pandas as pd
from typing import Any, Dict, Optional
from infra.gmo.gmo_auth import GmoAuth

# ロギングの設定
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ハンドラの設定
handler = RotatingFileHandler('trading.log', maxBytes=5 * 1024 * 1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())

class Strategy2(GmoAuth):
    """
    取引戦略を定義するクラス。
    """
    def __init__(self, symbol: str, equity_fraction: float = 0.7):
        super().__init__()
        self.symbol = symbol
        self.equity_fraction = equity_fraction
        self.position: Optional[Dict[str, Any]] = None

        try:
            market_info = self.fetch_symbols()
            self.min_order_size = market_info['minOrderSize']
            self.size_step = market_info['sizeStep']
            if self.size_step <= 0:
                raise ValueError('size_step must be greater than zero.')
        except Exception as e:
            logger.error(f'マーケット情報の取得に失敗しました: {e}')
            self.min_order_size = 0
            self.size_step = 0

    def calculate_position_size(self, balance_jpy: float, current_price: float) -> float:
        """
        ポジションサイズを計算する。
        """
        try:
            # すべての関連変数をfloatに変換
            balance_jpy = float(balance_jpy)
            current_price = float(current_price)
            self.equity_fraction = float(self.equity_fraction)
            self.min_order_size = float(self.min_order_size)
            self.size_step = float(self.size_step)
            
            # ポジションサイズの計算
            size = (balance_jpy * self.equity_fraction) / current_price
            adjusted_size = max(self.min_order_size, size - (size % self.size_step))
            adjusted_size = round(adjusted_size, 6)
            
            logger.debug(f'計算されたサイズ: {size}, 調整後サイズ: {adjusted_size}')
            return adjusted_size
        except ValueError as ve:
            logger.error(f'数値への変換に失敗しました: {ve}')
            return 0.0
        except Exception as e:
            logger.error(f'ポジションサイズの計算に失敗しました: {e}')
            return 0.0

    def generate_order(self, direction: str, latest_data: pd.DataFrame, prediction: float) -> Optional[Dict[str, Any]]:
        """
        指定された方向（'long' または 'short'）に基づいて注文を生成する。
        """
        df = latest_data
        idx = len(df) - 1
        atr_value = df['ATR'].iloc[idx]
        current_price = df['Close'].iloc[idx]
        balance_jpy = self.fetch_balance()
        atr_ratio = 0.5

        if direction == 'long':
            threshold = 0.05
            condition = prediction > threshold
            signal = 'ロング'
            price_direction = -1  # Buy below current price
        elif direction == 'short':
            threshold = -0.05
            condition = prediction < threshold
            signal = 'ショート'
            price_direction = 1  # Sell above current price
        else:
            logger.error(f'無効な方向指定: {direction}')
            return None

        logger.info(f'{signal}戦略 - Prediction: {prediction}, ATR: {atr_value}, Close: {current_price}, Balance: {balance_jpy} JPY')

        if self.size_step <= 0:
            logger.error('size_step が無効です。')
            return None

        # 指値価格を計算
        limit_price_dist = atr_value * atr_ratio
        limit_price_dist = max(1, round(limit_price_dist / self.size_step) * self.size_step)
        target_price = current_price + (limit_price_dist * price_direction)
        opposite_price = current_price - (limit_price_dist * price_direction)

        logger.debug(f'指値距離: {limit_price_dist}, 指値価格: {target_price}')

        if condition:
            if not self.position:
                self.cancel_order()
                size = self.calculate_position_size(balance_jpy, current_price)
                self.position = {'type': direction, 'price': target_price, 'size': size}

                logger.info(f'{signal}ポジションを開くシグナルを生成しました - 価格: {target_price}, サイズ: {size}')

                side = 'buy' if direction == 'long' else 'sell'
                return {
                    'symbol': self.symbol,
                    'side': side,
                    'amount': size,
                    'price': target_price,
                }
            else:
                logger.info('既にポジションを保有しています。保持中です。')
        else:
            if self.position and self.position['type'] == direction:
                self.cancel_order()
                
                logger.info(f'ポジションをクローズするシグナルを生成しました - 価格: {opposite_price}, サイズ: {self.position["size"]}')
                
                position_size = self.position['size']
                
                self.position = None

                side = 'sell' if direction == 'long' else 'buy'
                return {
                    'symbol': self.symbol,
                    'side': side,
                    'amount': position_size,
                    'price': opposite_price,
                }
            else:
                self.cancel_order()
                logger.info(f'シグナルありだが、クローズする {signal} ポジションがありません。')
        return None

    def execute(self, latest_data: pd.DataFrame, prediction: float) -> Optional[Dict[str, Any]]:
        """
        戦略を実行し、必要な注文を出す。
        ロングおよびショートの条件を評価し、それぞれに応じて注文を生成します。
        """
        order = None

        # ロング戦略の条件を評価
        long_threshold = 0.02
        if prediction > long_threshold or (self.position and self.position['type'] == 'long'):
            long_order = self.generate_order('long', latest_data, prediction)
            if long_order:
                order = long_order  # 戦略v001が単一の注文を返す場合

        # ショート戦略の条件を評価
        short_threshold = -0.02
        if prediction < short_threshold or (self.position and self.position['type'] == 'short'):
            short_order = self.generate_order('short', latest_data, prediction)
            if short_order:
                order = short_order  # 戦略v001が単一の注文を返す場合

        print(order)
        return order  # 単一の注文辞書またはNoneを返す
