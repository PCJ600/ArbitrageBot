from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import MemoryJobStore
from app.query.query_funds import monitor_funds_and_notify
import threading
import logging
import atexit

logger = logging.getLogger('app')

class Cronjobs:
    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Cronjobs, cls).__new__(cls)
                cls._instance._init_lock = threading.Lock()
        return cls._instance

    def __init__(self):
        # 双重检查锁定模式
        if not self._initialized:
            with self._init_lock:
                if not self._initialized:
                    self.scheduler = None
                    self._initialized = True

    def register_all_cronjobs(self):
        with self._init_lock:
            if self.scheduler is not None:
                logger.warning("Cronjobs already registered")
                return

            try:
                self.scheduler = BackgroundScheduler()
                self.scheduler.add_jobstore(MemoryJobStore(), 'default')
                self.scheduler.add_job(
                    id="fund_monitor",  # 建议指定唯一ID
                    func=monitor_funds_and_notify,
                    trigger='interval',
                    minutes=7,
                    replace_existing=True
                )
                self.scheduler.start()
                atexit.register(self.shutdown)  # 确保程序退出时关闭
                logger.info("Cronjobs registered successfully")
            except Exception as e:
                logger.critical(f"Cronjob registration failed: {str(e)}")
                raise

    def shutdown(self):
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Cronjobs shutdown gracefully")

def register_cronjobs():
    Cronjobs().register_all_cronjobs()
