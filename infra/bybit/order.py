    
import ccxt
import os
import logging
from logging.handlers import RotatingFileHandler

from infra.bybit.auth import BybitAuth   
from infra.bybit.trader import BybitTrader


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ハンドラの設定
handler = RotatingFileHandler('logs/trading.log', maxBytes=5 * 1024 * 1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())
    
class BybitOrder(BybitAuth):
    def __init__(self):
        super().__init__()
        
        self.min_order_size = 0.000048
        self.bybit_trader = BybitTrader()
        
        
    def _calculate_position_size(self, current_price: float, min_size: float) -> float:
        """
        ポジションサイズを計算する。
        """
        try:
            # すべての関連変数をfloatに変換
            #FIXME: balance_jpyの型が不明
            balance_jpy = float(self.bybit_trader.fetch_balance()['JPY'])
            current_price = float(current_price)
            self.equity_fraction = float(self.equity_fraction)
            self.size_step = float(min_size)
            
            # ポジションサイズの計算
            size = (balance_jpy * self.equity_fraction) / current_price
            adjusted_size = max(self.size_step, size - (size % self.size_step))
            adjusted_size = round(adjusted_size, 6)
            
            logger.debug(f'計算されたサイズ: {size}, 調整後サイズ: {adjusted_size}')
            return adjusted_size
        except ValueError as ve:
            logger.error(f'数値への変換に失敗しました: {ve}')
            return 0.0
        except Exception as e:
            logger.error(f'ポジションサイズの計算に失敗しました: {e}')
            return 0.0
    
    def create_limit_order(self, side, price):
        """
        指値注文を実行します。
        side: 'buy' または 'sell' の文字列を指定します。
        amount: 注文する数量（例: 0.001 BTC）。
        price: 注文する価格。
        """
        
        amount = self._calculate_position_size(price, self.min_order_size)
        
        if side == 'buy':
            order = self.exchange.create_limit_buy_order(self.symbol, amount, price)
        elif side == 'sell':
            order = self.exchange.create_limit_sell_order(self.symbol, amount, price)
        else:
            raise ValueError("sideには 'buy' または 'sell' を指定してください。")
        
        # FIXME: 戻り値未確認
        return order
    
    def create_close_order(self, side, price, amount):
        """
        決済注文を実行します。
        side: 'buy' または 'sell' の文字列を指定します。
        amount: 注文する数量（例: 0.001 BTC）。
        price: 注文する価格。
        """
        
        if side == 'buy':
            order = self.exchange.create_limit_buy_order(self.symbol, amount, price)
        elif side == 'sell':
            order = self.exchange.create_limit_sell_order(self.symbol, amount, price)
        else:
            raise ValueError("sideには 'buy' または 'sell' を指定してください。")