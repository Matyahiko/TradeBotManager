import ccxt
import time
import os
import sys


root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)

from infra.bybit.auth import BybitAuth

class BybitTrader(BybitAuth):
    def __init__(self):
        super().__init__()
    
    def fetch_balance(self):
        """
        残高を取得します。
        """
        try:
            balance = self.exchange.fetch_balance()["free"]
            
            return balance
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return None
        
    def fetch_symbols(self):
        """
        取引可能なシンボル情報を取得します。
        """
        try:
            symbols = self.exchange.fetch_markets()
            return symbols
        except Exception as e:
            print(f"Error fetching symbols: {e}")
            return None
    
    def fetch_ticker(self):
        """
        ティッカー情報を取得します。
        """
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            ticker = {
                'symbol': ticker['symbol'],
                'open': ticker['open'],
                'high': ticker['high'],
                'low': ticker['low'],
                'close': ticker['close'],
                'volume': ticker['baseVolume'],
                'bid': ticker['bid'],
                'ask': ticker['ask']
            }
            return ticker
        except Exception as e:
            print(f"Error fetching ticker: {e}")
            return None
        
    def cancel_all_orders(self):
        """
        すべてのオープン注文をキャンセルします。
        """
        try:
            # すべてのオープン注文を取得
            open_orders = self.exchange.fetch_open_orders()

            # 各注文をキャンセル
            for order in open_orders:
                order_id = order['id']
                self.cansel_order(order_id)

            print(f"{len(open_orders)} 注文のキャンセルが完了")

        except Exception as e:
            print(f"注文のキャンセルでエラー: {e}")

if __name__ == "__main__":
    
    balance = BybitTrader().fetch_balance()
    print("\n==== Balance ====")
    print(balance)
    
    # symbols = BybitAuth().fetch_symbols()
    # print("\n==== Symbols ====")
    # print(symbols)
    
    ticker = BybitTrader().fetch_ticker()
    print("\n==== Ticker ====")
    print(ticker)
    
    
    
    