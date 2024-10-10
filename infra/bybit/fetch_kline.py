import time
import pandas as pd
from datetime import datetime, timedelta, timezone
from infra.bybit.auth import BybitAuth

class BybitKlineDataFetcher(BybitAuth):
    def __init__(self):
        super().__init__()
        
        
    
    def fetch_ohlcv(self):
        """
        OHLCVデータを取得します。
        """
  
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe)
        for candle in ohlcv:
            print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(candle[0] / 1000))}, "
                    f"Open: {candle[1]}, High: {candle[2]}, Low: {candle[3]}, Close: {candle[4]}, Volume: {candle[5]}")
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            
            df.set_index('timestamp', inplace=True)
            return df

# 動作確認
if __name__ == "__main__":
    df = BybitKlineDataFetcher().fetch_ohlcv()
    print(df)