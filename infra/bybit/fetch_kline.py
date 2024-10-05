import time
import pandas as pd
from infra.bybit.auth import BybitAuth

class fetch_kline(BybitAuth):
    def __init__(self):
        super().__init__()
        
    
    def fetch_ohlcv(self):
        """
        OHLCVデータを取得します。
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe)
            for candle in ohlcv:
                print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(candle[0] / 1000))}, "
                        f"Open: {candle[1]}, High: {candle[2]}, Low: {candle[3]}, Close: {candle[4]}, Volume: {candle[5]}")
                
                kline = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
                
                
        except Exception as e:
            print(f"Error fetching OHLCV data: {e}")
            return None
        

# 使用例
if __name__ == "__main__":
    fetch_kline().fetch_ohlcv()