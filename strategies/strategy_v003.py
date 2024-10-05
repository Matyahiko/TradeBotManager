# strategy_v003.py
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

class Strategy3(GmoAuth):
    """
    取引戦略を定義するクラス（RSI抜き）。
    """
    def __init__(self, symbol: str, equity_fraction: float = 0.7):
        super().__init__()
        self.symbol = symbol
        self.equity_fraction = equity_fraction
        self.position: Optional[Dict[str, Any]] = None
        self.trading_count = 0

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
            balance_jpy = float(balance_jpy['JPY'])
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

    def generate_order(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        注文を生成する。
        """
        if signal is not None:
            return {
                'symbol': self.symbol,
                'side': signal['side'],
                'amount': signal['amount'],
                'price': signal['price'],
            }
        else:
            return None

    def long_short_atr_strategy(self, latest_data: pd.DataFrame, prediction: float):
        """
        ロングおよびショート戦略を実行する（RSI抜き）。
        """
        self.long_atr_strategy(latest_data, prediction)
        self.short_atr_strategy(latest_data, prediction)

    def long_atr_strategy(self, latest_data: pd.DataFrame, prediction: float) -> Optional[Dict[str, Any]]:
        """
        ATRを用いたロング戦略を実行する。
        """
        df = latest_data
        idx = len(df) - 1
        atr_value = df['ATR'].iloc[idx]
        
        current_price = df['Close'].iloc[idx]
        balance_jpy = self.fetch_balance()
        long_threshold = 0.01
        atr_ratio = 0.9

        logger.info(f'ロング戦略 - Prediction: {prediction}, ATR: {atr_value}, Close: {current_price}, Balance: {balance_jpy} JPY')

        if self.size_step <= 0:
            logger.error('size_step が無効です。')
            return None

        # 指値価格を計算
        limit_price_dist = atr_value * atr_ratio
        limit_price_dist = max(1, round(limit_price_dist / self.size_step) * self.size_step)
        buy_price = current_price - limit_price_dist

        logger.debug(f'ロング指値距離: {limit_price_dist}, 指値価格: {buy_price}')

        # RSIの条件を削除し、予測値のみを使用
        if prediction > long_threshold:
            self.trading_count += 1
            logger.info(f'ロング trading_count: {self.trading_count}')
            # 買いシグナル
            if not self.position:
                self.cancel_order()
                size = self.calculate_position_size(balance_jpy, current_price)
                self.position = {'side': 'buy', 'price': buy_price, 'size': size}

                logger.info(f'長期ポジションを開くシグナルを生成しました - 価格: {buy_price}, サイズ: {size}')

                self.generate_order({
                    'symbol': self.symbol,
                    'side': 'buy',
                    'amount': size,
                    'price': buy_price,
                })
                
            else:
                if self.position['side'] == 'buy':
                    logger.info('既にロングポジションを保有しています。保持中です。')
                else:
                    logger.info('ショートポジションを保有中のため、ロングポジションは開けません。')
        else:
            if self.position and self.position['side'] == 'buy':
                # ポジションをクローズするシグナル
                self.cancel_order()
                balance = self.fetch_balance() 
                position_size = float(balance['BTC']) 
                position_size = position_size - (position_size % self.size_step)  # 小数部分の切り捨て
                logger.info(f'ロングポジションをクローズするシグナルを生成しました - 価格: {current_price + limit_price_dist}, サイズ: {self.position["size"]}')
                self.position = None

                return {
                    'symbol': self.symbol,
                    'side': 'sell',
                    'amount': position_size,
                    'price': current_price + limit_price_dist,
                }
            else:
                logger.info('ロング売りシグナルありだが、クローズするロングポジションがありません。')

        return None

    def short_atr_strategy(self, latest_data: pd.DataFrame, prediction: float) -> Optional[Dict[str, Any]]:
        """
        ATRを用いたショート戦略を実行する。
        """
        df = latest_data
        idx = len(df) - 1
        atr_value = df['ATR'].iloc[idx]
        
        current_price = df['Close'].iloc[idx]
        balance_jpy = self.fetch_balance()
        short_threshold = -0.01
        atr_ratio = 0.9

        logger.info(f'ショート戦略 - Prediction: {prediction}, ATR: {atr_value}, Close: {current_price}, Balance: {balance_jpy} JPY')

        if self.size_step <= 0:
            logger.error('size_step が無効です。')
            return None

        # 指値価格を計算
        limit_price_dist = atr_value * atr_ratio
        limit_price_dist = max(1, round(limit_price_dist / self.size_step) * self.size_step)
        sell_price = current_price + limit_price_dist

        logger.debug(f'ショート指値距離: {limit_price_dist}, 指値価格: {sell_price}')

        # RSIの条件を削除し、予測値のみを使用
        if prediction < short_threshold:
            self.trading_count += 1
            logger.info(f'ショート trading_count: {self.trading_count}')
            # 売りシグナル
            if not self.position:
                self.cancel_order()
                size = self.calculate_position_size(balance_jpy, current_price)
                self.position = {'side': 'sell', 'price': sell_price, 'size': size}

                logger.info(f'短期ポジションを開くシグナルを生成しました - 価格: {sell_price}, サイズ: {size}')

                self.generate_order({
                    'symbol': self.symbol,
                    'side': 'sell',
                    'amount': size,
                    'price': sell_price,
                })
                
            else:
                if self.position['side'] == 'sell':
                    logger.info('既にショートポジションを保有しています。保持中です。')
                else:
                    logger.info('ロングポジションを保有中のため、ショートポジションは開けません。')
        else:
            if self.position and self.position['side'] == 'sell':
                # ポジションをクローズするシグナル
                self.cancel_order()
                balance = self.fetch_balance() 
                position_size = float(balance['BTC']) 
                position_size = position_size - (position_size % self.size_step)  # 小数部分の切り捨て
                logger.info(f'Sホートポジションをクローズするシグナルを生成しました - 価格: {current_price - limit_price_dist}, サイズ: {self.position["size"]}')
                self.position = None

                return {
                    'symbol': self.symbol,
                    'side': 'buy',
                    'amount': position_size,
                    'price': current_price - limit_price_dist,
                }
            else:
                logger.info('ショート買いシグナルありだが、クローズするショートポジションがありません。')

        return None
