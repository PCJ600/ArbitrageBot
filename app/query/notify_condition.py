import logging
from datetime import datetime
from typing import Dict, List, Tuple, Set

logger = logging.getLogger('app')

FUND_REDEMPTION_FEES = {
    '501305': 0.1,
    '501306': 0.1,
    '501307': 0.1,
    '164705': 0.0,
    '501310': 0.5,
    '501301': 0.5,
    '501302': 0.5,
    '160924': 0.5,
    '160717': 0.5,
    '161831': 0.5
}

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

    def is_full_open(apply_status: str) -> bool:
        """判断是否开放申购（完全开放）"""
        return apply_status not in ['暂停申购']
    
    def is_limited_open(apply_status: str) -> bool:
        """判断是否小额开放申购"""
        return apply_status not in ['暂停申购', '开放申购']
    
    def is_redeemable(redeem_status: str) -> bool:
        """判断是否开放赎回"""
        return "开放赎回" in redeem_status
    
    def is_significant_discount(fund_id: str, premium: float) -> bool:
        """
        判断是否有显著折价（用于套利）
        
        参数说明:
        - fund_id: 基金代码
        - premium: 溢价率（不带百分号，如-1.0表示1%折价）
        
        返回:
        - True: 当折价空间（考虑赎回费后）足够
        - False: 不满足条件
        """
        # 获取该基金的赎回费率（不带百分号），如果没有则使用默认阈值1%
        redemption_fee = FUND_REDEMPTION_FEES.get(fund_id, None)
        
        if redemption_fee is not None:
            # 指定基金：要求折价 > (赎回费 + 0.6%)
            required_discount = redemption_fee + 0.6
        else:
            # 非指定基金：默认要求折价 > 1%
            required_discount = 1.0
        
        # premium是负值表示折价，所以判断是否小于负的required_discount
        return premium < -required_discount

    # 对于持有的基金
    if is_holding:
        # 盘中溢价>5%通知
        if not is_near_close and premium_rate > 5.0:
            return True
        
        # 临近收盘溢价>1.1%且开放申购，通知一次
        if is_near_close and premium_rate > 1.1 and is_full_open(apply_status):
            return True
        
        # 临近收盘可以折价套利，通知一次
        if is_near_close and is_redeemable(redeem_status) and is_significant_discount(fund_id, premium_rate):
            return True
    
    # 对于未持有的基金
    else:
        # 仅临近收盘溢价>5%且开放申购（小额），通知一次
        if is_near_close and premium_rate > 5.0 and is_limited_open(apply_status):
            return True
    
    return False
