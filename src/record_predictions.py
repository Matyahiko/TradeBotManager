# record_predictions.py

import os
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import logging

# ロギングの設定
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def record_prediction(prediction, csv_file='strage/tmp/predictions.csv', plot_file='strage/prediction_distribution_deploy.png'):
    """
    予測値をCSVファイルに記録し、分布をプロットして画像として保存します。

    Args:
        prediction (float): 記録する予測値。
        csv_file (str): 予測値を記録するCSVファイルのパス。
        plot_file (str): 分布図を保存する画像ファイルのパス。
    """
    try:
        # CSVファイルに予測値を追加
        file_exists = os.path.isfile(csv_file)
        with open(csv_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['prediction'])  # ヘッダーの追加
            writer.writerow([prediction])
        logger.debug(f"Prediction {prediction} recorded in {csv_file}.")

        # 全ての予測値を読み込む
        predictions = []
        with open(csv_file, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    pred = float(row['prediction'])
                    predictions.append(pred)
                except ValueError:
                    logger.warning(f"Invalid prediction value skipped: {row['prediction']}")
                    continue  # 無効なエントリをスキップ

        if not predictions:
            logger.warning("No valid predictions to plot.")
            return

        # 予測値の分布をプロット
        plt.figure(figsize=(10, 6))
        sns.histplot(predictions, kde=True, bins=30)
        plt.title('Prediction Distribution')
        plt.xlabel('Prediction')
        plt.ylabel('Frequency')

        # プロットを画像として保存
        plt.savefig(plot_file)
        plt.close()
        logger.debug(f"Prediction distribution saved as {plot_file}.")

    except Exception as e:
        logger.error(f"Error in record_prediction: {e}")
