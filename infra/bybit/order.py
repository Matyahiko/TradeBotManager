    
import ccxt
import os

from infra.bybit.auth import BybitAuth   
    
class BybitOrder(BybitAuth):
    def __init__(self):
        super().__init__()
    
    def create_market_buy_order(self, amount):
        """
        成り行き注文を実行します。
        side: 'buy' または 'sell' の文字列を指定します。
        amount: 注文する数量（例: 0.001 BTC）。
        """
        order = self.exchange.create_market_order(self.symbol,amount)
        #FIXME: 戻り値未確認
        return order
        
    def create_market_sell_order(self, amount):
        """
        成り行き注文を実行します。
        side: 'buy' または 'sell' の文字列を指定します。
        amount: 注文する数量（例: 0.001 BTC）。
        """
        order = self.exchange.create_market_order(self.symbol, amount)
        #FIXME: 戻り値未確認
        return order

    def create_limit_buy_order(self, amount, price):
        """
        指値注文を実行します。
        side: 'buy' または 'sell' の文字列を指定します。
        amount: 注文する数量（例: 0.001 BTC）。
        price: 注文する価格。
        """
        order = self.exchange.create_limit_buy_order(self.symbol, amount, price)
        #FIXME: 戻り値未確認
        return order

    def create_limit_sell_order(self, amount, price):
        """
        指値注文を実行します。
        side: 'buy' または 'sell' の文字列を指定します。
        amount: 注文する数量（例: 0.001 BTC）。
        price: 注文する価格。
        """
        order = self.exchange.create_limit_sell_order(self.symbol, amount, price)