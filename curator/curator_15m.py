import ccxt
import pandas as pd
import time
import os
import matplotlib.pyplot as plt
from datetime import datetime
from infra.bybit.auth import BybitAuth


class BybitFetcher(BybitAuth):
    def __init__(self):
        super().__init__()

    def fetch_latest_ohlcv(self, limit=200):
        """
        最新のOHLCVデータを取得します。

        :param limit: 取得するローソク足の数（デフォルトは200）
        :return: pandas DataFrame
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=self.timeframe, limit=limit)
            df = self._ohlcv_to_dataframe(ohlcv)
            return df
        except ccxt.BaseError as error:
            print(f"エラーが発生しました: {error}")
            return pd.DataFrame()

    def fetch_all_ohlcv(self, since=None, limit=200):
        """
        指定した開始時刻から現在までのすべてのOHLCVデータを取得します。

        :param since: 開始時刻（ミリ秒）。デフォルトはexchangeのデフォルト。
        :param limit: 一度に取得するローソク足の数（デフォルトは200）
        :return: pandas DataFrame
        """
        all_ohlcv = []
        try:
            while True:
                print(f"Fetching OHLCV data since {since} with limit {limit}")
                ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=self.timeframe, since=since, limit=limit)
                print(f"Fetched {len(ohlcv)} candles")
                if not ohlcv:
                    print("No more data to fetch.")
                    break
                all_ohlcv += ohlcv
                last_timestamp = ohlcv[-1][0]
                since = last_timestamp + 1  # 次のデータ取得のために1ミリ秒追加
                # BybitのAPI制限を避けるために少し待機
                time.sleep(self.exchange.rateLimit / 1000)
        except ccxt.BaseError as error:
            print(f"エラーが発生しました: {error}")

        df = self._ohlcv_to_dataframe(all_ohlcv)
        print(f"Total candles fetched: {len(df)}")
        return df

    def _ohlcv_to_dataframe(self, ohlcv):
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df.set_index('timestamp', inplace=True)
        # タイムスタンプをUTCに変換する部分を削除
        df.index = pd.to_datetime(df.index, unit='ms')
        return df

    def save_to_csv_pkl(self, df, filename='bybit_15m_kline'):
        # ディレクトリが存在しない場合は作成
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        df.to_csv(filename + '.csv')
        df.to_pickle(filename + '.pkl')
        print(f"データを{filename}に保存しました。")
        
    def plot_ohlcv(self, df):
        df['Close'].plot(figsize=(12, 6), title='BTC/USD Close Price')
        plt.savefig('strage/btc_usd_close_price.png')


# 使用例
if __name__ == "__main__":
    fetcher = BybitFetcher()
    #FIXME: 長期間のデータを取得できない
    # 取得開始日を日付で指定できるように変更
    start_date_str = '2023-01-01'  
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        since = int(start_date.timestamp() * 1000)
        print(f"Fetching data since: {start_date.isoformat()} ({since})")
    except ValueError as ve:
        print(f"日付の形式が正しくありません: {ve}")
        exit(1)
    
    all_df = fetcher.fetch_all_ohlcv(since=since)
    print("すべてのデータ:")
    print(all_df)
    
    # データをCSVに保存
    fetcher.save_to_csv_pkl(all_df, 'strage/bybit_15m_kline')
    
    # データをプロット
    fetcher.plot_ohlcv(all_df)
