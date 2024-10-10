#strategy_v001.py
import logging
import numpy as np
import pandas as pd
from typing import Any, Dict, Optional
from infra.bybit.auth import BybitAuth

# ロギングの設定
from logging.handlers import RotatingFileHandler
from infra.bybit.trader import BybitTrader
from infra.bybit.order import BybitOrder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ハンドラの設定
handler = RotatingFileHandler('trading.log', maxBytes=5 * 1024 * 1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())

class Strategy(BybitAuth):
    """
    取引戦略を定義するクラス。
    """
    def __init__(self, symbol: str, order_size: float):
        super().__init__()
        self.symbol = symbol
        self.order_size = order_size
        self.bybit_trader = BybitTrader()
        self.bybit_order = BybitOrder()
        self.position: Optional[Dict[str, Any]] = None
        self.trading_count = 0
    
    def long_atr_strategy(self, latest_data: pd.DataFrame, prediction) -> Optional[Dict[str, Any]]:
        """
        ATRを用いたロング戦略を実行する。
        """
        
        #TODO: data[(data['RSI'] < 30) & (data['RSI'].shift(1) >= 30)]　RSIの条件を追加する

        df = latest_data
        idx = len(df) - 1
        atr_value = df['ATR'].iloc[idx]
        rsi_value = df['RSI'].iloc[idx]
        
        current_price = df['Close'].iloc[idx]
        balance_jpy = self.fetch_balance()
        long_threshold = 0.01
        short_threshold = -0.01
        atr_ratio = 0.95

        logger.info(f'最新データ - Prediction: {prediction}, ATR: {atr_value}, Close: {current_price}, Balance: {balance_jpy} USD')

        # 指値価格を計算
        limit_price_dist = atr_value * atr_ratio
        buy_price = int(current_price - limit_price_dist)
        sell_price = int(current_price + limit_price_dist)

        logger.debug(f'指値距離: {limit_price_dist}, 指値価格: {buy_price}')

        if prediction > long_threshold:
            self.trading_count += 1
            logger.info(f'trading_count: {self.trading_count}')
            #買いシグナル
            if not self.position:
                self.cancel_order()
                logger.info(f'longシグナルを生成しました - 価格: {buy_price}')
                #注文を作成
                BybitOrder.create_limit_order(self.bybit_order, 'buy', buy_price)
            else:
                logger.info('既にポジションを保有しています。保持中です。')
        else:
            if self.position:
                self.cancel_order()
                position_size = float(self.bybit_trader.fetch_balance()['BTC']) 
                position_size = position_size - (position_size % self.order_size)  # 小数部分の切り捨て
                logger.info(f'ポジションをクローズするシグナルを生成しました - 価格: {sell_price}, サイズ: {position_size}')
                self.position = None

                BybitOrder.create_close_order(self.bybit_order, 'sell', sell_price, position_size)
            else:
                self.cancel_order()
                logger.info('売りシグナルありだが、クローズするポジションがありません。')
