from datetime import datetime, time
import chinese_calendar
import logging
import pytz
logger = logging.getLogger('app')

china_tz = pytz.timezone('Asia/Shanghai')

def is_trading_time():
    now = datetime.now(china_tz)
    current_time = now.time()
    current_date = now.date()

    logger.debug('time: %r, date: %r', current_time, current_date)

    if now.weekday() >= 5:
        return False

    if chinese_calendar.is_holiday(current_date):
        return False

    # A-share trading time 9:30-11:30, 13:00-15:00
    trading_morning_start = time(9, 30)
    trading_morning_end = time(11, 30)
    trading_afternoon_start = time(13, 0)
    trading_afternoon_end = time(15, 0)
    return (trading_morning_start <= current_time <= trading_morning_end) or (trading_afternoon_start <= current_time <= trading_afternoon_end)


def is_near_close():
    start_time = time(14, 30)
    end_time = time(14, 50)
    now = datetime.now(china_tz).time()
    return start_time <= now <= end_time
