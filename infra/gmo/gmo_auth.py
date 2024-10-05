import requests
import hmac
import hashlib
import time
import os
import logging
import json
from typing import Any, Dict
from dotenv import load_dotenv
from datetime import datetime

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GmoAuth:
    """
    GMOコインのAPI認証とデータ取得を行うクラス。
    """
    def __init__(self, symbol_str: str = 'BTC'):
        # 環境変数のロード
        load_dotenv(".environment/.env")

        # 環境変数からAPIキーとシークレットキーを取得
        self.api_key = os.getenv('GMO_API_KEY')
        self.secret_key = os.getenv('GMO_SECRET_KEY')
        self.symbol_str = symbol_str

        # APIキーとシークレットキーが存在するか確認
        if not self.api_key or not self.secret_key:
            logger.error("APIキーまたはシークレットキーが環境変数に設定されていません。")
            raise ValueError("APIキーまたはシークレットキーが見つかりません。")

    def _create_headers(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        text = timestamp + method + path + body
        sign = hmac.new(
            self.secret_key.encode('ascii'),
            text.encode('ascii'),
            hashlib.sha256
        ).hexdigest()

        return {
            "API-KEY": self.api_key,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign
        }

    def fetch_balance(self) -> Dict[str, Any]:
        """
        アカウントの残高を取得する。
        """
        try:
            method = 'GET'
            endPoint = 'https://api.coin.z.com/private'
            path = '/v1/account/assets'
            headers = self._create_headers(method, path)
            response = requests.get(endPoint + path, headers=headers)

            if response.status_code == 200:
                balance = response.json()
                for item in balance['data']:
                    if item['symbol'] == 'JPY':
                        return item['amount']
                return balance
            else:
                logger.error(f"残高の取得に失敗しました: {response.status_code} {response.text}")
                response.raise_for_status()

        except Exception as e:
            logger.exception("残高取得中にエラーが発生しました。")
            raise e

    def fetch_symbols(self) -> Dict[str, Any]:
        """
        取引可能なシンボル情報を取得する。
        """
        try:
            endPoint = 'https://api.coin.z.com/public'
            path = '/v1/symbols'
            response = requests.get(endPoint + path)

            if response.status_code == 200:
                symbols = response.json()
                for symbol in symbols['data']:
                    if symbol['symbol'] == f'{self.symbol_str}':
                        return {
                            'symbol': symbol['symbol'],
                            'minOrderSize': float(symbol['minOrderSize']),
                            'sizeStep': float(symbol['sizeStep'])
                        }
            else:
                logger.error(f"シンボルの取得に失敗しました: {response.status_code} {response.text}")
                response.raise_for_status()

        except Exception as e:
            logger.exception("シンボル取得中にエラーが発生しました。")
            raise e

    def fetch_ticker(self) -> Dict[str, Any]:
        """
        現在のティッカー情報を取得する。
        """
        try:
            endPoint = 'https://api.coin.z.com/public'
            path = f'/v1/ticker?symbol={self.symbol_str}'
            response = requests.get(endPoint + path).json()
            data = response['data'][0]
            return {'bid': data['bid'], 'ask': data['ask']}

        except Exception as e:
            logger.exception("ティッカー情報取得中にエラーが発生しました。")
            raise e
    
    def cancel_order(self) -> Dict[str, Any]:
        try:
            method = 'POST'
            endPoint = 'https://api.coin.z.com/private'
            path = '/v1/cancelBulkOrder'
            reqBody = {
                'symbols': [self.symbol_str],
            }
            body = json.dumps(reqBody)
            headers = self._create_headers(method, path, body)

            response = requests.post(endPoint + path, headers=headers, data=body)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"注文のキャンセルに失敗しました: {response.status_code} {response.text}")
                response.raise_for_status()

        except Exception as e:
            logger.exception("注文キャンセル中にエラーが発生しました。")
            raise e

    def check_executions(self) -> Dict[str, Any]:
        #FIXME: この関数は確認していない
        try:
            method = 'GET'
            endPoint = 'https://api.coin.z.com/private'
            path = '/v1/activeOrders'
            reqBody = {
                'symbol': self.symbol_str,
                "page": 1
            }
            body = json.dumps(reqBody)
            headers = self._create_headers(method, path, body)

            response = requests.post(endPoint + path, headers=headers, data=body)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"ポジションの取得に失敗しました: {response.status_code} {response.text}")
                response.raise_for_status()

        except Exception as e:
            logger.exception("ポジションの取得に中にエラーが発生しました。")
            raise e
        

if __name__ == "__main__":
    try:
        auth = GmoAuth()
        symbol_info = auth.fetch_symbols()
        print("\n=== シンボル情報 ===")
        print(symbol_info)

        ticker = auth.fetch_ticker()
        print("\n=== ティッカー情報 ===")
        print(ticker)
        
        # cancel_order = auth.cancel_order()
        # print("\n=== 注文キャンセル ===")
        # print(cancel_order)
        
        active_order = auth.check_executions()
        print("\n=== 約定情報 ===")
        print(active_order)
        
        # balance = auth.fetch_balance()
        # print("\n=== 残高情報 ===")
        # print(balance)

    except Exception as e:
        logger.error(f"プログラムがエラーで終了しました: {e}")
