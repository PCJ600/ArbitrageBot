import json
import random
import requests
import time
import logging
import traceback
from datetime import date
from django.db.models import F
from django.db import connection

from app.query.trading_time import is_trading_time
from app.models import FundNotification
from app.notify.notify import notify_handler
from app.query.ashare_lof import get_ashare_lof_notify_list
from app.query.qdii import get_qdii_notify_list

logger = logging.getLogger('app')

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

def monitor_funds_and_notify():
    logger.debug("query funds start...")
    connection.close_if_unusable_or_obsolete()

    if not is_trading_time():
        logger.debug("not trading time")
        return

    lof_list = get_ashare_lof_notify_list()
    all_lofs = lof_list['stock_lof'] + lof_list['index_lof']
    qdii_list = get_qdii_notify_list()
    all_qdiis = qdii_list['hk_qdii'] + qdii_list['us_qdii'] + qdii_list['commodity_qdii']

    all_funds = all_lofs + all_qdiis
    for fund in all_funds:
        fund_id, premium_rate, apply_status, redeem_status = fund
        title = fund_id
        msg = f"{premium_rate:.2f}% {apply_status} {redeem_status}"

        if has_notified_today(fund_id):
            continue

        add_notify_count_to_DB(fund_id)
        logger.info(f"Funds Notification - title: {title}, message: {msg}")
        notify_handler.send_message(msg, title)

    logger.debug("query funds end...")
