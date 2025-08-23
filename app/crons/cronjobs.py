from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import MemoryJobStore

from app.query.query_funds import monitor_funds_and_notify

import time
import threading
import logging
logger = logging.getLogger('app')

# refer to https://apscheduler.readthedocs.io/en/latest/userguide.html
class Cronjobs:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Cronjobs, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.scheduler = None

    def register_all_cronjobs(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_jobstore(MemoryJobStore(), 'default')
        self.scheduler.add_job(id="", func=monitor_funds_and_notify, trigger='interval', minutes=7, replace_existing=True)
        self.scheduler.start()


def register_cronjobs():
    c = Cronjobs()
    c.register_all_cronjobs()
    logger.info("register cronjobs done")
