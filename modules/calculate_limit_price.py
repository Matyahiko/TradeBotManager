from modules.logging_config import logging_config
from typing import Tuple 

class LimitPrice(Tuple):
    bby_price: int
    sell_price: int

def calculate_limit_price_dist(self, current_price: float, atr_value: float, atr_ratio: float) -> LimitPrice:
        """
        指値距離と指値価格を計算する。
        """
        limit_price_dist = atr_value * atr_ratio
        buy_price = int(current_price - limit_price_dist)
        sell_price = int(current_price + limit_price_dist)
        
        self.logger.debug(f'指値距離: {limit_price_dist}, 指値価格: {buy_price}')
        
        return LimitPrice(buy_price=buy_price, sell_price=sell_price)


        
        
        
        