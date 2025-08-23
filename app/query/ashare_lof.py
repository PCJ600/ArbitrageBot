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
HOLDING_FUNDS = {'160632'}

def query_stock_lof() -> Optional[Dict]:
    """
    获取股票型LOF数据
    :param page: 页码
    :param rp: 每页记录数
    :return: 返回JSON数据或None
    """
    base_url = "https://www.jisilu.cn/data/lof/stock_lof_list/"
    timestamp = int(time.time() * 1000)
    params = {
        "___jsl": f"LST___t={timestamp}",
    }
    return _query_lof_data(base_url, params)


def query_index_lof(page: int = 1, rp: int = 25) -> Optional[Dict]:
    """
    获取指数型LOF数据
    :param page: 页码
    :param rp: 每页记录数
    :return: 返回JSON数据或None
    """
    base_url = "https://www.jisilu.cn/data/lof/index_lof_list/"
    timestamp = int(time.time() * 1000)
    params = {
        "___jsl": f"LST___t={timestamp}",
    }
    return _query_lof_data(base_url, params)


def _query_lof_data(base_url: str, params: Dict) -> Optional[Dict]:
    """
    内部方法，用于实际请求LOF数据
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Referer": "https://www.jisilu.cn/data/lof/",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        # "Cookie": "auto_reload_qdiia=true; kbz_newcookie=1; kbzw__user_login=your_cookie_value_here" # 如果需要登录
    }

    try:
        resp = requests.get(base_url, headers=headers, params=params, timeout=(10, 30))
        if resp.status_code == 200:
            content = resp.content
            content_size = len(content)
            if content_size > 1024 * 1024:
                raise ValueError(f'resp oversize: {content_size} bytes')

            data = json.loads(content)
            logger.debug("query lof data: %r", data)
            return data
        else:
            logger.error("Query lof failed, url: %r, http_code: %r", base_url, resp.status_code)
            return None
    except Exception as e:
        logger.error("Query lof failed: %r, tb: %r", e, traceback.format_exc())
        return None


def process_lof_data(data: Dict) -> List[Tuple[str, float, str, str]]:
    """
    处理LOF数据，筛选可套利的基金
    
    :param data: 原始LOF数据
    :return: [(fund_id, 溢价率, 申购状态, 是否持有)]
    """
    notify_list = []
    if not data or 'rows' not in data:
        logger.info("无有效LOF数据或数据格式错误")
        return notify_list
    
    near_close = is_near_close()
    logger.info("\n" + "="*80)
    logger.info("开始处理LOF数据（临近收盘: %s）", "是" if near_close else "否")
    logger.info("-"*80)
    
    for row in data['rows']:
        item = row.get('cell', {})
        fund_id = item.get('fund_id', '未知基金')
        fund_name = item.get('fund_nm', '未知名称')
        
        try:
            # 处理折价率数据
            discount_str = item.get('discount_rt', '0').strip()
            if discount_str in ('-', 'N/A', ''):
                #logger.info("| %-8s | %-16s | 无效折价率: %-5s | 已跳过", 
                #           fund_id, fund_name, discount_str)
                continue
                
            discount_rate = float(discount_str)
            premium_rate = discount_rate
        
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
                #logger.info(log_msg + " ❌ 不满足条件")
                pass
                
        except (ValueError, TypeError) as e:
            logger.info("| %-8s | %-16s | 数据解析失败: %-20s |", 
                       fund_id, fund_name, str(e)[:20])
            continue
    
    logger.info("-"*80)
    logger.info("处理完成，共发现 %d 个可套利基金", len(notify_list))
    logger.info("="*80 + "\n")
    return notify_list

def get_notify_list() -> Dict[str, List[Tuple[str, float, str, str]]]:
    """
    获取需要通知的LOF列表
    :return: 字典，包含stock_lof和index_lof两个键
    """
    result = {
        'stock_lof': [],
        'index_lof': []
    }

    # 获取股票型LOF数据
    stock_data = query_stock_lof()
    if stock_data:
        result['stock_lof'] = process_lof_data(stock_data)

    # 获取指数型LOF数据
    index_data = query_index_lof()
    if index_data:
        result['index_lof'] = process_lof_data(index_data)

    return result
