import json
import random
import requests
import time
import logging
import traceback
from app.query.validate_data import parse_fund_data
from app.query.trading_time import is_trading_time, is_near_market_close

# TODO: limit JSON data size (no more than 1M)

logger = logging.getLogger('app')
HOLDINGS = {'501302', '160924', '164705',
            '501305', '501306', '501307',
            '159333'}
def get_default_holdings():
    return HOLDINGS


def query_qdii_data():
    base_url = "https://www.jisilu.cn/data/qdii/qdii_list/A"
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
        # "Cookie": "auto_reload_qdiia=true; kbz_newcookie=1; kbzw__user_login=your_cookie_value_here" # TODO: Maybe we need to login jisilu
    }
    
    try:
        resp = requests.get(base_url, headers=headers, params=params, timeout=(10,30))
        if resp.status_code == 200:
            data = resp.json()
            return data
        else:
            logger.error("Query qdii failed, http_code: %r", resp.status_code)
            return None
    except Exception as e:
        logger.error("Query qdii failed: %r, tb: %r", e, traceback.format_exc())
        return None




# TODO
def notify_to_my_phone(fund_list):
    pass


# TODO
def has_notified_today(fund_id):
    pass


"""
如果LOF/ETF出现溢价交易机会, 通知到手机
* 对于持有的基金
  * 盘中溢价>5%, 通知一次
  * 临近收盘溢价>1.2%且开放申购, 通知一次
* 对于未持有的基金
  * 盘中不通知
  * 临近收盘溢价>5%且小额开放申购, 通知一次

* 一天通知次数不超过XX次
"""
def notify_if_premium(funds_dict):
    my_holdings = get_default_holdings()
    funds_need_notify = []
    try:
        for fund_id, fund in funds_dict.items():
            discount_rt = fund.get('discount_rt')
            apply_status = fund.get('apply_status')
            logger.info("key: %r, discount: %r, apply_status: %r", fund_id, discount_rt, apply_status)

            if fund_id in my_holdings:
                if not is_near_market_close():
                    if discount_rt > 0.05:
                        funds_need_notify.append(fund)
                else:
                    if discount_rt > 0.011:
            else:
                if not is_near_market_close():
                    continue
                if discount_rt > 0.05:
                    funds_need_notify.append(fund)

        notify_to_my_phone(funds_need_notify)
    except Exception as e:
        logger.error("notify failed %r, tb: %r", e, traceback.format_exc())


def test_data():
    import ast
    try:
        qdii_data = None
        with open('/test_qdii_data.txt', 'r', encoding='utf-8') as file:
            content = file.read()
            qdii_data = ast.literal_eval(content)
        return qdii_data
    except Exception as e:
        print('exception:', e)
        return None


def query_funds():
    logger.debug("query funds begin")
    """
    if not is_trading_time():
        logger.debug("not trading time")
        return

    time.sleep(random.randint(0, 60))

    raw_data = query_qdii_data()
    """
    raw_data = test_data()
    if not raw_data:
        logger.error("query fund data failed")
        return

    funds_dict = parse_fund_data(raw_data)
    if not funds_dict:
        logger.error("parse fund data failed")
        return

    notify_if_premium(funds_dict)

"""
if __name__ == "__main__":
    pass
    data = query_qdii_data()
    if data:
        print(data)
    test_data()
"""
