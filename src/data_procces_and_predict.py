#data_procces_and_predict.py
import os
import logging
import pandas as pd
from catboost import CatBoostRegressor
from calc_technical_indicators import calc_technical_indicators
from infra.gmo.gmo_data_fetcher import GmoDataFetcher

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 設定クラス
class Config:
    MODEL_DIR = os.path.join('models')
    OUTPUT_DIR = os.path.join('Storage', 'predictions')

def load_model() -> CatBoostRegressor:
    model_path = os.path.join(Config.MODEL_DIR, 'simple_catboost_model.cbm')
    
    if not os.path.exists(model_path):
        logger.error(f"モデルファイルが存在しません: {model_path}")
        raise FileNotFoundError(f"モデルファイルが存在しません: {model_path}")
    
    model = CatBoostRegressor()
    model.load_model(model_path)
    
    return model

def predict_and_save(df) -> float:
    """
    最新のデータを用いて予測を行い、結果を保存する関数
    """
    model = load_model()
    latest_row = df.iloc[[-1]]
    
    # 特徴量名を保持するために values を使用しない
    X = latest_row 
    
    prediction = model.predict(X)[0]
    prediction_value = float(prediction)
    
    return prediction_value

if __name__ == "__main__":
    # データの取得と前処理
    df = GmoDataFetcher().fetch_ohlcv(symbol='BTC/JPY', timeframe='15m', limit=100)
    df = calc_technical_indicators(df)
    
    # 予測の実行
    result = predict_and_save()
    logger.info(f"返された予測結果: {result}")
