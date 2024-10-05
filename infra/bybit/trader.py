import ccxt
import time
import os

from infra.bybit.auth import BybitAuth

class BybitTrader(BybitAuth):
    def __init__(self):
        super().__init__()
    
    def fetch_balance(self):
        """
        Bybitの残高を取得します。
        """
        try:
            balance = self.exchange.fetch_balance()
            print("Balance:", balance['total'])
            return balance['total']
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return None
    
    def fetch_ticker(self):
        """
        ティッカー情報を取得します。
        """
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            print("Ticker:", ticker)
            return ticker
        except Exception as e:
            print(f"Error fetching ticker: {e}")
            return None
        
    def cancel_all_order(self):
        """
        注文をキャンセルします。
        """
        try:
            result = self.exchange.cancel_all_orders(self.symbol)
            print("Order canceled:", result)
            return result
        except Exception as e:
            print(f"Error canceling order: {e}")
            return None

    def fetch_open_orders(self):
        
        try:
            orders = self.exchange.fetch_open_orders(self.symbol)
            print("Open orders:", orders)
            return orders
        except Exception as e:
            print(f"Error fetching open orders: {e}")
            return None
        
    def fetch_position(self):
        """
        未約定の注文を取得します。
        """
        try:
            orders = self.exchange.fetch_open_orders(self.symbol)
            print("Open orders:", orders)
            return orders
        except Exception as e:
            print(f"Error fetching open orders: {e}")
            return None

# 使用例
if __name__ == "__main__":
    trader = BybitTrader()
    # 残高の取得
    balance = trader.fetch_balance()
    print(balance)