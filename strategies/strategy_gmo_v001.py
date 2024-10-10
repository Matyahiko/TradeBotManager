#strategy_v001.py
import logging
from typing import Any, Dict, Optional
import asyncio

import numpy as np
import pandas as pd

from infra.gmo.gmo_auth import GmoAuth
from infra.gmo.gmo_order import GmoCoin
from infra.gmo.gmo_websocket_client import websocket_order_events
from modules.logging_config import logging_config
from modules.calculate_position import calculate_position_size
from modules.calculate_limit_price import calculate_limit_price_dist
from modules.calculate_limit_price import LimitPrice



class Strategy(GmoAuth, GmoCoin):
    """
    取引戦略を定義するクラス。
    """
    def __init__(self, symbol: str, equity_fraction: float = 0.7):
        super().__init__()
        self.symbol = symbol
        self.equity_fraction = equity_fraction
        self.position: Optional[Dict[str, Any]] = None
        self.trading_count = 0
        self.logger = logging_config.getLogger(__name__)
        market_info = self.fetch_symbols()
        self.min_order_size = market_info['minOrderSize']
        self.size_step = market_info['sizeStep']
        self.reverse_side = 'buy'
        

    def long_atr_strategy(self, latest_data: pd.DataFrame, prediction: float) -> Optional[Dict[str, Any]]:
        """
        ATRを用いたロング戦略を実行する。
        """
        
        #TODO: data[(data['RSI'] < 30) & (data['RSI'].shift(1) >= 30)]　RSIの条件を追加する

        df = latest_data
        idx = len(df) - 1
        atr_value = df['ATR'].iloc[idx]
        rsi_value = df['RSI'].iloc[idx]
        current_price = df['Close'].iloc[idx]
        balance_jpy = self.fetch_balance()["JPY"]
        long_threshold = 0.01
        atr_ratio = 0.3
        limit_price = calculate_limit_price_dist(current_price=current_price, atr_value=atr_value, atr_ratio=atr_ratio)
        former_size = float(self.fetch_balance()['BTC'])
        former_size = former_size - (former_size % self.size_step)  # 小数部分の切り捨て
        
        
        #FIXME: floatの精度問題で最後に小さい値が残ることがある
        former_size = round(former_size, 4)
        self.logger.info(f'最新データ - Prediction: {prediction}, ATR: {atr_value}, Close: {current_price}, Balance: {balance_jpy} JPY, limit_price: {limit_price}')
        self.cancel_order()
        self.limit_order(symbol=self.symbol, side=self.reverse_side, amount=size, price=limit_price.buy_price)
        
        asyncio.run(websocket_order_events())
       
    
        if prediction > long_threshold:
            self.trading_count += 1
            self.reverse_side = 'sell'
            self.logger.info(f'trading_count: {self.trading_count}')
            #買いシグナル

            size = self.calculate_position_size(balance_jpy, current_price, self.equity_fraction, self.min_order_size, self.size_step)
            self.logger.info(f'longポジションを開くシグナルを生成しました - 価格: {limit_price.buy_price}, サイズ: {size}')

            self.limit_order(
                symbol=self.symbol,
                side='buy',
                amount=size,
                price=limit_price.buy_price
            )       
        else:
            self.logger.info(f'閾値未満のため、取引は行いませんでした。')



