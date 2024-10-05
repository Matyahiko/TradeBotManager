import aiohttp
import pandas as pd
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)

class GmoDataFetcher:
    """
    GMOコインからデータを非同期で取得するクラス。
    """
    def __init__(self, proxy: str = None):
        self.RestAPI_url = 'https://api.coin.z.com/public'
        self.proxy = proxy

    async def fetch_kline_data(self, symbol: str, interval: str) -> pd.DataFrame:
        #FIXME
        # JSTタイムゾーンを設定
        jst = timezone(timedelta(hours=9))
        logger.info(f"JSTタイムゾーン: {jst}")
        # 現在の日時を取得
        current_time = datetime.now(jst)
        logger.info(f"現在の日時: {current_time}")
        # 過去2日分の日付を取得
        date_list = [(current_time - timedelta(days=i)).strftime('%Y%m%d') for i in range(2)]
        date_list.reverse()  # 日付を古い順に並べ替え

        url = f"{self.RestAPI_url}/v1/klines"
        all_data = []

        async with aiohttp.ClientSession() as session:
            for date_str in date_list:
                params = {
                    'symbol': symbol,
                    'interval': interval,
                    'date': date_str
                }
                async with session.get(url, params=params, proxy=self.proxy) as response:
                    response.raise_for_status()
                    ohlcv_data = await response.json()
                    if 'data' in ohlcv_data:
                        all_data.extend(ohlcv_data['data'])
                    else:
                        logger.warning(f"データが存在しません: {date_str}")

        if not all_data:
            logger.error("取得したデータが空です。")
            return pd.DataFrame()  # 空のデータフレームを返す

        df = pd.DataFrame(
            all_data,
            columns=['openTime', 'open', 'high', 'low', 'close', 'volume']
        )
        df.columns = ['openTime', 'Open', 'High', 'Low', 'Close', 'Volume']
        df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)
        df['openTime'] = df['openTime'].astype(int)
        df['DateTime'] = df['openTime'].apply(self._convert_unix_time_to_datetime)

        # 'openTime' 列を削除
        df.drop('openTime', axis=1, inplace=True)

        # 必要に応じてJSTに変換
        df['DateTime'] = df['DateTime'].dt.tz_convert(jst)

        # 日付でソート（重要）
        df.sort_values('DateTime', inplace=True)

        # 列の順序を変更（オプション）
        cols = ['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume']
        df = df[cols]

        # 'DateTime' 列をインデックスに設定
        df.set_index('DateTime', inplace=True)

        # 連続性を確認
        expected_interval = pd.Timedelta('15min')
        time_diffs = df.index.to_series().diff().dropna()
        gaps = time_diffs[time_diffs != expected_interval]


        # if not gaps.empty:
        #     print("[yellow]データにギャップがあります。ギャップの場所と時間差:[/yellow]")
        #     print(gaps)
        # else:
        #     print("[green]データは連続しています。[/green]")

        return df

    
    @staticmethod
    def _convert_unix_time_to_datetime(unix_time):
        """
        UNIXエポックタイムをUTCの日時に変換する。
        """
        if isinstance(unix_time, str):
            unix_time = int(unix_time)
        return datetime.fromtimestamp(unix_time / 1000, tz=timezone.utc)

import asyncio
from rich import print

async def main():
    proxy = 'http://wwwproxy.osakac.ac.jp:8080'
    fetcher = GmoDataFetcher(proxy=proxy)

    try:
        ohlcv_data = await fetcher.fetch_kline_data(symbol='BTC', interval='15min')

        if ohlcv_data is not None and not ohlcv_data.empty:
            print("[blue]OHLCV Data (最後の100行のみ, DateTimeをJSTに変換済み):[/blue]")
            print(ohlcv_data)
        else:
            print("[red]データが取得できませんでした。[/red]")
    except Exception as e:
        print(f"[red]エラーが発生しました: {e}[/red]")

if __name__ == '__main__':
    asyncio.run(main())
