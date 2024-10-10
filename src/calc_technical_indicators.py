# calc_technical_indicators.py
import talib
import pandas as pd


def calc_technical_indicators(df):
        # テクニカル指標を追加
        open, high, low, close, volume = df["Open"], df["High"], df["Low"], df["Close"], df["Volume"]
        hilo = (df['High'] + df['Low']) / 2
        # 価格(hilo または close)を引いた後、価格(close)で割ることで標準化
        df['BBANDS_upperband'], df['BBANDS_middleband'], df['BBANDS_lowerband'] = talib.BBANDS(close, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
        df['BBANDS_upperband'] = (df['BBANDS_upperband'] - hilo) / close
        df['BBANDS_middleband'] = (df['BBANDS_middleband'] - hilo) / close
        df['BBANDS_lowerband'] = (df['BBANDS_lowerband'] - hilo) / close
        df['DEMA'] = (talib.DEMA(close, timeperiod=30) - hilo) / close
        df['EMA'] = (talib.EMA(close, timeperiod=30) - hilo) / close
        df['HT_TRENDLINE'] = (talib.HT_TRENDLINE(close) - hilo) / close
        df['KAMA'] = (talib.KAMA(close, timeperiod=30) - hilo) / close
        df['MA'] = (talib.MA(close, timeperiod=30, matype=0) - hilo) / close
        df['MIDPOINT'] = (talib.MIDPOINT(close, timeperiod=14) - hilo) / close
        df['SMA'] = (talib.SMA(close, timeperiod=30) - hilo) / close
        df['T3'] = (talib.T3(close, timeperiod=5, vfactor=0) - hilo) / close
        df['TEMA'] = (talib.TEMA(close, timeperiod=30) - hilo) / close
        df['TRIMA'] = (talib.TRIMA(close, timeperiod=30) - hilo) / close
        df['WMA'] = (talib.WMA(close, timeperiod=30) - hilo) / close
        df['LINEARREG'] = (talib.LINEARREG(close, timeperiod=14) - close) / close
        df['LINEARREG_INTERCEPT'] = (talib.LINEARREG_INTERCEPT(close, timeperiod=14) - close) / close


        # 価格(close)で割ることで標準化
        df['AD'] = talib.AD(high, low, close, volume) / close
        df['ADOSC'] = talib.ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10) / close
        df['APO'] = talib.APO(close, fastperiod=12, slowperiod=26, matype=0) / close
        df['HT_PHASOR_inphase'], df['HT_PHASOR_quadrature'] = talib.HT_PHASOR(close)
        df['HT_PHASOR_inphase'] /= close
        df['HT_PHASOR_quadrature'] /= close
        df['LINEARREG_SLOPE'] = talib.LINEARREG_SLOPE(close, timeperiod=14) / close
        df['MACD_macd'], df['MACD_macdsignal'], df['MACD_macdhist'] = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        df['MACD_macd'] /= close
        df['MACD_macdsignal'] /= close
        df['MACD_macdhist'] /= close
        df['MINUS_DM'] = talib.MINUS_DM(high, low, timeperiod=14) / close
        df['MOM'] = talib.MOM(close, timeperiod=10) / close
        df['OBV'] = talib.OBV(close, volume) / close
        df['PLUS_DM'] = talib.PLUS_DM(high, low, timeperiod=14) / close
        df['STDDEV'] = talib.STDDEV(close, timeperiod=5, nbdev=1) / close
        df['TRANGE'] = talib.TRANGE(high, low, close) / close


        df['ADX'] = talib.ADX(high, low, close, timeperiod=14)
        df['ADXR'] = talib.ADXR(high, low, close, timeperiod=14)
        df['AROON_aroondown'], df['AROON_aroonup'] = talib.AROON(high, low, timeperiod=14)
        df['AROONOSC'] = talib.AROONOSC(high, low, timeperiod=14)
        df['BOP'] = talib.BOP(open, high, low, close)
        df['CCI'] = talib.CCI(high, low, close, timeperiod=14)
        df['DX'] = talib.DX(high, low, close, timeperiod=14)
        # skip MACDEXT MACDFIX たぶん同じなので
        df['MFI'] = talib.MFI(high, low, close, volume, timeperiod=14)
        df['MINUS_DI'] = talib.MINUS_DI(high, low, close, timeperiod=14)
        df['PLUS_DI'] = talib.PLUS_DI(high, low, close, timeperiod=14)
        df['RSI'] = talib.RSI(close, timeperiod=14)
        df['STOCH_slowk'], df['STOCH_slowd'] = talib.STOCH(high, low, close, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        df['STOCHF_fastk'], df['STOCHF_fastd'] = talib.STOCHF(high, low, close, fastk_period=5, fastd_period=3, fastd_matype=0)
        df['STOCHRSI_fastk'], df['STOCHRSI_fastd'] = talib.STOCHRSI(close, timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
        df['TRIX'] = talib.TRIX(close, timeperiod=30)
        df['ULTOSC'] = talib.ULTOSC(high, low, close, timeperiod1=7, timeperiod2=14, timeperiod3=28)
        df['WILLR'] = talib.WILLR(high, low, close, timeperiod=14)

        df['ATR'] = talib.ATR(high, low, close, timeperiod=14)
        df['NATR'] = talib.NATR(high, low, close, timeperiod=14)

        df['HT_DCPERIOD'] = talib.HT_DCPERIOD(close)
        df['HT_DCPHASE'] = talib.HT_DCPHASE(close)
        df['HT_SINE_sine'], df['HT_SINE_leadsine'] = talib.HT_SINE(close)
        df['HT_TRENDMODE'] = talib.HT_TRENDMODE(close)

        df['BETA'] = talib.BETA(high, low, timeperiod=5)
        df['CORREL'] = talib.CORREL(high, low, timeperiod=30)

        df['LINEARREG_ANGLE'] = talib.LINEARREG_ANGLE(close, timeperiod=14)
        
        df.dropna(inplace=True)
        
        return df