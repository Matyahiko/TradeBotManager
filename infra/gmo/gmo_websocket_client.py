# websocket_client.py

import asyncio
import os
import logging
from pybotters import Client
from pybotters.helpers import GMOCoinHelper
from datetime import datetime, timezone
from dotenv import load_dotenv

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def websocket_main():
    load_dotenv(".environment/.env")  # 環境変数のロード

    apis = {
        "gmocoin": [
            os.getenv("GMO_API_KEY", ""),
            os.getenv("GMO_SECRET_KEY", ""),
        ],
    }

    async with Client(apis=apis) as client:
        store = client.store  # データストアの取得

        # GMOCoinHelperのインスタンスを作成
        gmohelper = GMOCoinHelper(client)

        try:
            # POST /private/v1/ws-auth のエイリアス
            token = await gmohelper.create_access_token()

            ws = client.ws_connect(
                # Private WebSocket URLを構築
                f"wss://api.coin.z.com/ws/private/v1/{token}",
                send_json={
                    "command": "subscribe",
                    "channel": "orderEvents",
                    "option": "PERIODIC",
                },
                hdlr_json=store.onmessage,
            )

            # WebSocket URLとアクセストークンを管理するタスクを作成
            asyncio.create_task(
                gmohelper.manage_ws_token(ws, token),
            )

            logger.info("=== WebSocket接続を開始しました。 ===")
            logger.info("ポジションサマリーイベントを待機中...")

            async with store.position_summary.watch() as stream:
                async for change in stream:
                    print(f"[{datetime.now(timezone.utc).isoformat()}] {change.data}")

        except Exception as e:
            logger.error(f"WebSocket接続中にエラーが発生しました: {e}")
