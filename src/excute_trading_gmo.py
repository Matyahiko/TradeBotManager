import schedule
import time
import asyncio
import sys
import os
import logging
import argparse

# パスの設定（必要に応じて調整）
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 必要なモジュールのインポート
from calc_technical_indicators import calc_technical_indicators
from infra.gmo.gmo_data_fetcher import GmoDataFetcher
from data_procces_and_predict import predict_and_save
from strategies.strategy_gmo_v001 import Strategy 

from infra.gmo.gmo_auth import GmoAuth
from infra.gmo.gmo_order import GmoCoin


# record_predictions.py から関数をインポート
from src.record_predictions import record_prediction

# ロギングの設定
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# GMO認証とプロキシの設定
auth = GmoAuth()
proxy = ''
proxies = {
    "http": proxy,
    "https": proxy
}

symbol = 'BTC'
gmo_coin = GmoCoin(proxies=proxies)  # TODO: 通常環境用にoptionalにする
fetcher = GmoDataFetcher(proxy=proxy)
strategy = Strategy(symbol=symbol, equity_fraction=0.7)


async def trade():
    try:
        symbols = auth.fetch_symbols()
        logger.debug(f"Fetched symbols: {symbols}")

        df = await fetcher.fetch_kline_data(symbol=symbol, interval='15min')
        df = calc_technical_indicators(df)
        prediction = predict_and_save(df)

        record_prediction(prediction)

        # Strategy1 のインスタンスを使用して execute メソッドを呼び出す
        strategy.long_atr_strategy(df, prediction)

    except Exception as e:
        logger.error(f"トレード中にエラーが発生しました: {e}")

async def execute_trade_async():
    await trade()

def execute_trade():
    asyncio.run(execute_trade_async())

def parse_arguments():
    parser = argparse.ArgumentParser(description="GMOトレーディングスクリプト")
    parser.add_argument(
        '-i', '--immediate',
        action='store_true',
        help='スケジュール開始前にトレードを即時実行します'
    )
    return parser.parse_args()

# スケジュールの設定
schedule_times = ["00:05", "15:05", "30:05", "45:05"]  
for t in schedule_times:
    schedule.every().hour.at(t).do(execute_trade)

if __name__ == "__main__":
    args = parse_arguments()

    if args.immediate:
        logger.info("即時実行オプションが指定されたため、トレードを即時実行します。")
        execute_trade()

    logger.info("スケジューリングを開始します。")
    while True:
        schedule.run_pending()
        time.sleep(1)
