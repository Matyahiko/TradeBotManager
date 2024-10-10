# modules/logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """
    ロガーを設定して返します。
    
    :param name: ロガーの名前
    :param log_file: ログファイルのパス
    :param level: ログレベル
    :return: 設定されたロガー
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # ハンドラの設定
    handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # 既にハンドラが設定されていない場合のみ追加
    if not logger.handlers:
        logger.addHandler(handler)
        logger.addHandler(logging.StreamHandler())
    
    return logger
