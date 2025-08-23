import logging
from datetime import datetime
from typing import Dict, List, Tuple, Set

logger = logging.getLogger('app')

# 硬编码持有的基金列表

def check_notify_condition(
    fund_id: str,
    premium_rate: float,
    apply_status: str,
    redeem_status: str,
    is_near_close: bool,
    is_holding: bool
) -> bool:
    """
    检查是否符合通知条件（区分持有和未持有的基金）
    
    :param fund_id: 基金ID
    :param premium_rate: 溢价率（正数表示溢价，负数表示折价）
    :param apply_status: 申购状态
    :param is_near_close: 是否临近收盘
    :return: 是否满足通知条件
    """

    def is_open_to_invest(status: str) -> bool:
        """判断是否开放申购（完全开放）"""
        return apply_status not in ['暂停申购']
    
    def is_limited_open(status: str) -> bool:
        """判断是否小额开放申购"""
        return apply_status not in ['暂停申购', '开放申购']
    
    def is_redeemable(status: str) -> bool:
        """判断是否开放赎回"""
        return "开放赎回" in status
    
    def is_significant_discount(premium: float) -> bool:
        """判断是否有显著折价（用于套利）"""
        return premium < -1.0  # 折价超过1%

    is_near_close = True # TODO: remove it
    is_holding = True # TODO: remove it 
    if premium_rate < 3: # TODO: remove it
        return False

    # 对于持有的基金
    if is_holding:
        # 盘中溢价>5%通知
        if not is_near_close and premium_rate > 5.0:
            return True
        
        # 临近收盘溢价>1.1%且开放申购，通知一次
        if is_near_close and premium_rate > 1.1 and is_open_to_invest(apply_status):
            return True
        
        # 临近收盘可以折价套利，通知一次
        if is_near_close and is_redeemable(redeem_status) and is_significant_discount(premium_rate):
            return True
    
    # 对于未持有的基金
    else:
        # 仅临近收盘溢价>5%且开放申购（小额），通知一次
        if is_near_close and premium_rate > 5.0 and is_limited_open(apply_status):
            return True
    
    return False
