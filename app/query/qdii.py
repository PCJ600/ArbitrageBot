import json
import logging
import requests
import time
import traceback
from typing import Dict, List, Tuple, Optional
from app.query.trading_time import is_near_close
from app.query.notify_condition import check_notify_condition

logger = logging.getLogger('app')

# 硬编码持有的基金列表
HOLDING_FUNDS = {'160924', '164705', '160717', '161831', '501301', '501302', '501305', '501306', '501307', '501310'}

def query_hk_qdii() -> Optional[Dict]:
    """获取港股QDII数据"""
    return query_specific_qdii("https://www.jisilu.cn/data/qdii/qdii_list/A")

def query_us_qdii() -> Optional[Dict]:
    """获取美股QDII数据"""
    return query_specific_qdii("https://www.jisilu.cn/data/qdii/qdii_list/E")

def query_commodity_qdii() -> Optional[Dict]:
    """获取大宗商品QDII数据"""
    return query_specific_qdii("https://www.jisilu.cn/data/qdii/qdii_list/C")

def query_specific_qdii(base_url: str) -> Optional[Dict]:
    """
    获取特定类型的QDII数据
    :param base_url: 基础URL
    :return: 返回JSON数据或None
    """
    timestamp = int(time.time() * 1000)
    params = {
        "___jsl": f"LST___t={timestamp}",
        "only_lof": "y",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Referer": "https://www.jisilu.cn/data/qdii/",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
    }

    try:
        resp = requests.get(base_url, headers=headers, params=params, timeout=(10, 30))
        if resp.status_code == 200:
            content = resp.content
            content_size = len(content)
            if content_size > 1024 * 1024:
                raise ValueError(f'resp oversize: {content_size} bytes')

            data = json.loads(content)
            logger.debug("query qdii data: %r", data)
            return data
        else:
            logger.error("Query qdii failed, url: %r, http_code: %r", base_url, resp.status_code)
            return None
    except Exception as e:
        logger.error("Query qdii failed: %r, tb: %r", e, traceback.format_exc())
        return None


def process_qdii_data(data: Dict) -> List[Tuple[str, float, str, str]]:
    """
    处理QDII数据，筛选可套利的基金
    
    :param data: 原始QDII数据
    :return: [(fund_id, 溢价率, 申购状态, 赎回状态)]
    """
    notify_list = []
    if not data or 'rows' not in data:
        logger.info("无有效QDII数据或数据格式错误")
        return notify_list
    
    near_close = is_near_close()
    logger.info("\n" + "="*80)
    logger.info("开始处理QDII数据（临近收盘: %s）", "是" if near_close else "否")
    logger.info("-"*80)
    
    for row in data['rows']:
        item = row.get('cell', {})
        fund_id = item.get('fund_id', '未知基金')
        fund_name = item.get('fund_nm', '未知名称')
        
        try:
            # 处理溢价率数据（可能包含百分号）
            discount_str = item.get('discount_rt', '0').strip()
            if discount_str in ('-', 'N/A', '', '--'):
                discount_rate = 0.0
            else:
                # 移除百分号并转换为浮点数
                discount_rate = float(discount_str.replace('%', ''))
            
            premium_rate = discount_rate
        
            # 获取申购和赎回状态
            apply_status = item.get('apply_status', '未知状态')
            redeem_status = item.get('redeem_status', '未知状态')
            is_holding = fund_id in HOLDING_FUNDS
            
            # 结构化日志输出
            log_msg = (
                f"| {fund_id:8} | {fund_name:16} | "
                f"溢价: {premium_rate:6.2f}% | "
                f"申购: {apply_status:8} | "
                f"赎回: {redeem_status:8} | "
                f"{'持有' if is_holding else '未持有':4} |"
            )
            
            if check_notify_condition(
                fund_id=fund_id,
                premium_rate=premium_rate,
                apply_status=apply_status,
                redeem_status=redeem_status,
                is_near_close=near_close,
                is_holding=is_holding
            ):
                logger.info(log_msg + " ✅ 需通知")
                notify_list.append((fund_id, premium_rate, apply_status, redeem_status))
            else:
                logger.debug(log_msg + " ❌ 不满足条件")
                
        except (ValueError, TypeError) as e:
            logger.warning("| %-8s | %-16s | 数据解析失败: %-20s | 原始数据: %s", 
                         fund_id, fund_name, str(e)[:20], str(item)[:50])
            continue
    
    logger.info("-"*80)
    logger.info("处理完成，共发现 %d 个可套利基金", len(notify_list))
    logger.info("="*80 + "\n")
    return notify_list

def get_qdii_notify_list() -> Dict[str, List[Tuple[str, float, str, str]]]:
    """
    获取需要通知的QDII列表
    :return: 字典，包含hk_qdii、us_qdii和commodity_qdii三个键
    """
    result = {
        'hk_qdii': [],
        'us_qdii': [],
        'commodity_qdii': []
    }

    # 获取港股QDII数据
    hk_data = query_hk_qdii()
    if hk_data:
        result['hk_qdii'] = process_qdii_data(hk_data)

    # 获取美股QDII数据
    us_data = query_us_qdii()
    if us_data:
        result['us_qdii'] = process_qdii_data(us_data)

    # 获取大宗商品QDII数据
    commodity_data = query_commodity_qdii()
    if commodity_data:
        result['commodity_qdii'] = process_qdii_data(commodity_data)

    return result
