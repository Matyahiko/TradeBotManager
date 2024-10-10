import ccxt
import os
from dotenv import load_dotenv

class BybitAuth:
    def __init__(self,symbol='BTC/USDT', timeframe='15m'):
        # 環境変数のロード
        load_dotenv(".environment_pr/.env")

        self.api_key = os.getenv('BYBIT_API_PUBLIC')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
    
        self.symbol = symbol
        self.timeframe = timeframe
        self.exchange = ccxt.bybit({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,  # レートリミットを有効化
        })
        
