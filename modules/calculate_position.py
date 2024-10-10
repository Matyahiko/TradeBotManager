import logging_config

logger = logging_config.getLogger(__name__)

def calculate_position_size(self, balance_jpy: float, current_price: float,equity_fraction: float, min_order_size: float,size_step :float = None) -> float:
        """
        ポジションサイズを計算する。
        """
        
        try:
            # すべての関連変数をfloatに変換
            balance_jpy = float(balance_jpy)
            current_price = float(current_price)
            equity_fraction = float(equity_fraction)
            min_order_size = float(min_order_size)
            size_step = float(self.size_step)
            
            # ポジションサイズの計算
            size = (balance_jpy * self.equity_fraction) / current_price
            adjusted_size = max(self.min_order_size, size - (size % self.size_step))
            #FIXME;roundの６を変更する
            adjusted_size = round(adjusted_size, 6)
            
            self.logger.debug(f'計算されたサイズ: {size}, 調整後サイズ: {adjusted_size}')
            return adjusted_size
        except ValueError as ve:
            self.logger.error(f'数値への変換に失敗しました: {ve}')
            return 0.0
        except Exception as e:
            self.logger.error(f'ポジションサイズの計算に失敗しました: {e}')
            return 0.0