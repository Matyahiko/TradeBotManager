import asyncio
import logging
import sys
import os

import requests
import json
import hmac
import hashlib
import time
from datetime import datetime

# パスの設定（必要に応じて調整）
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 必要なモジュールのインポート
from gmo_auth import GmoAuth

# ロギングの設定
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_order():
    # プロキシ設定が必要な場合はここで設定
    proxy = 'http://wwwproxy.osakac.ac.jp:8080'
    proxies = {
        "http": proxy,
        "https": proxy
    }

    # GMOの認証オブジェクトを作成
    auth = GmoAuth()
    symbols = auth.fetch_symbols()
    ticker = auth.fetch_ticker()
    bid = int(ticker['bid'])
    ask = int(ticker['ask'])
    size = symbols['minOrderSize']
    
    symbol = 'BTC'  # シンボルを指定
    side = 'BUY'    # 'BUY' または 'SELL'
    executionType = 'LIMIT'  # 'LIMIT' または 'MARKET'
    order_price = str(ask + 10)
    
    logger.info(f"order_price: {order_price}")
    logger.info(f"bid: {bid}")
    logger.info(f"ask: {ask}")
    logger.info(f"minOrderSize: {size}")

    

    apiKey    = auth.api_key
    secretKey = auth.secret_key

    timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
    method    = 'POST'
    endPoint  = 'https://api.coin.z.com/private'
    path      = '/v1/order'
    reqBody = {
        "symbol": symbol,
        "side": side,
        "executionType": executionType,
        "price": order_price,
        "size": size
    }

    text = timestamp + method + path + json.dumps(reqBody)
    sign = hmac.new(bytes(secretKey.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

    headers = {
        "API-KEY": apiKey,
        "API-TIMESTAMP": timestamp,
        "API-SIGN": sign
    }

    res = requests.post(endPoint + path, headers=headers, data=json.dumps(reqBody))
    print (json.dumps(res.json(), indent=2))

if __name__ == "__main__":
    asyncio.run(debug_order())
