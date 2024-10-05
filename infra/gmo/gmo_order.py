import logging
from typing import Any, Dict, Optional
import requests
import json
import hmac
import hashlib
import time
from datetime import datetime

from infra.gmo.gmo_auth import GmoAuth

logger = logging.getLogger(__name__)

class GmoCoin(GmoAuth):
    def __init__(self, proxies: Optional[Dict[str, str]] = None):
        super().__init__()
        self.proxies = proxies  # プロキシ設定を保存

    def limit_order(self, symbol: str, side: str, amount: float, price: float) -> Dict[str, Any]:
        url = "https://api.coin.z.com/private/v1/order"
        payload = {
            "symbol": f"{symbol}",
            "side": side.upper(),
            "executionType": "LIMIT",
            "timeInForce": "FAS",
            "price": str(int(price)),  # 小数点以下を削除
            "size": str(amount)  # 必要に応じてフォーマットを調整
            # 必要に応じて "losscutPrice": "30012" などの追加フィールドを含める
        }
        
        # タイムスタンプの生成（ミリ秒単位）
        timestamp = str(int(time.time() * 1000))
        method = 'POST'
        path = '/v1/order'
        
        # 署名用のテキストの作成
        text = timestamp + method + path + json.dumps(payload)
        
        # HMAC SHA256で署名を生成
        sign = hmac.new(
            self.secret_key.encode('ascii'),
            text.encode('ascii'),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            "API-KEY": self.api_key,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(payload),
                proxies=self.proxies,  # プロキシ設定を適用
                timeout=10  # 必要に応じてタイムアウトを設定
            )
            response.raise_for_status()  # HTTPエラーが発生した場合例外を投げる
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Limit order failed: {e}")
            return {"error": str(e)}
