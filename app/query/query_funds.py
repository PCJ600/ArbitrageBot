import json
import random
import requests
import time
import logging
import traceback
from datetime import date
from django.db.models import F

from app.query.validate_data import parse_fund_data
from app.query.trading_time import is_trading_time, is_near_market_close
from app.models import FundNotification
from app.notify.notify import notify_handler

logger = logging.getLogger('app')

MAX_QUERY_SIZE  = 1 * 1024 * 1024 # response size limits to 1 MB

HOLDINGS = {'501302', '160924', '164705', '501305', '501306', '501307'}
def get_default_holdings():
    return HOLDINGS



def query_qdii_data():
    try:
        hk_data = query_specific_qdii("https://www.jisilu.cn/data/qdii/qdii_list/A")
        us_data = query_specific_qdii("https://www.jisilu.cn/data/qdii/qdii_list/E")
        commodity_data = query_specific_qdii("https://www.jisilu.cn/data/qdii/qdii_list/C")

        logger.info("query qdii data, hk: %r, us: %r, co: %r", len(hk_data.get('rows')), len(us_data.get('rows')), len(commodity_data.get('rows')))

        qdii_data = {'rows': []}
        qdii_data['rows'].extend(hk_data.get('rows'))
        qdii_data['rows'].extend(us_data.get('rows'))
        qdii_data['rows'].extend(commodity_data.get('rows'))
        return qdii_data
    except Exception as e:
        logger.error("Query qdii data failed: %r, tb: %r", e, traceback.format_exc())
        return None

def query_specific_qdii(base_url):
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
        # "Cookie": "auto_reload_qdiia=true; kbz_newcookie=1; kbzw__user_login=your_cookie_value_here" # Maybe we need to login jisilu
    }

    try:
        time.sleep(random.uniform(3, 5))
        resp = requests.get(base_url, headers=headers, params=params, timeout=(10,30))
        if resp.status_code == 200:
            content = resp.content
            content_size = len(content)
            if content_size > MAX_QUERY_SIZE:
                raise ValueError('resp oversize: %r bytes', content_size)

            data = json.loads(content)
            logger.debug("query qdii data: %r", data)
            return data
        else:
            logger.error("Query qdii failed, url: %r, http_code: %r", base_url, resp.status_code)
            return None
    except Exception as e:
        logger.error("Query qdii failed: %r, tb: %r", e, traceback.format_exc())
        return None



def has_notified_today(fund_id):
    today = date.today()
    exists = FundNotification.objects.filter(fund_id=fund_id, notify_date=today).exists()
    return exists


def add_notify_count_to_DB(fund_id):
    today = date.today()
    queryset = FundNotification.objects.filter(fund_id=fund_id, notify_date=today)
    if queryset.exists():
        queryset.update(notify_count=F('notify_count') + 1)
    else:
        FundNotification.objects.create(fund_id=fund_id, notify_date=today, notify_count=1)

def decimal_to_percentage(decimal, decimals=2):
    percentage = decimal * 100
    formatted_percentage = f"{percentage:.{decimals}f}%"
    return formatted_percentage


# 每个基金代码当天最多通知一次, 一次通知最多20条记录
def notify_to_my_phone(fund_list):
    fund_list = sorted(fund_list, key=lambda x: x.get('discount_rt'), reverse=True)
    fund_list = fund_list[:20]
    if len(fund_list) == 0:
        return

    logger.info("%r funds need notify", len(fund_list))
    message_list = []
    try:
        for fund in fund_list:
            fund_id = fund.get('fund_id')
            add_notify_count_to_DB(fund_id)
            discount_percent = decimal_to_percentage(fund.get('discount_rt'))
            one_msg = '{} {} 溢价{} {}'.format(fund.get('fund_id'), fund.get('fund_nm'), discount_percent, fund.get('apply_status'))
            message_list.append(one_msg)

        for msg in message_list:
            notify_handler.send_message(msg)

    except Exception as e:
        logger.error("notify failed: %r, tb: %r", e, traceback.format_exc())


# apply_status maybe in ['限100', '开放申购', '限5千']
def open_to_investors(apply_status):
    return apply_status not in ['暂停申购']

def limited_open_to_investors(apply_status):
    return apply_status not in ['暂停申购', '开放申购']


# If LOF/ETF can arbitrage, notify to my phone.
def notify_if_premium(funds_dict):
    my_holdings = get_default_holdings()
    funds_need_notify = []
    try:
        for fund_id, fund in funds_dict.items():
            if has_notified_today(fund_id):
                continue

            discount_rt = fund.get('discount_rt')
            apply_status = fund.get('apply_status')
            logger.debug("fund_id: %r, discount: %r, apply_status: %r", fund_id, discount_rt, apply_status)

            if fund_id in my_holdings:
                # 对于持有的基金, 盘中溢价>5%通知一次; 临近收盘溢价>1.2%且开放申购, 通知一次
                if not is_near_market_close():
                    if discount_rt > 0.05:
                        funds_need_notify.append(fund)
                else:
                    if open_to_investors(apply_status) and discount_rt > 0.012:
                        funds_need_notify.append(fund)
            else:
                # 对于未持有的基金, 盘中不通知; 临近收盘时溢价>5%且小额开放申购, 通知一次
                if not is_near_market_close():
                    continue
                if limited_open_to_investors(apply_status) and discount_rt > 0.05:
                    funds_need_notify.append(fund)

        notify_to_my_phone(funds_need_notify)
    except Exception as e:
        logger.error("notify failed %r, tb: %r", e, traceback.format_exc())

def query_funds():
    """
    if not is_trading_time():
        logger.debug("not trading time")
        return

    time.sleep(random.randint(0, 60))
    """

    raw_data = query_qdii_data()
    if not raw_data:
        logger.error("query fund data failed")
        return

    funds_dict = parse_fund_data(raw_data)
    if not funds_dict:
        logger.error("parse fund data failed")
        return

    notify_if_premium(funds_dict)
