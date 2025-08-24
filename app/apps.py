# app/apps.py
import sys
import os
from django.apps import AppConfig
from django.core.checks import register, Error

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        if self._should_load_cronjobs():
            @register('cronjobs')
            def cronjob_check(**kwargs):
                try:
                    from app.crons.cronjobs import register_cronjobs
                    register_cronjobs()
                    return []  # 必须返回列表！
                except Exception as e:
                    return [Error(f"Cronjob failed: {str(e)}")]

    def _should_load_cronjobs(self):
        """判断是否加载 cronjobs"""
        if 'runserver' in sys.argv:
            return True
        try:
            import psutil
            return psutil.Process(os.getppid()).name() in ('gunicorn', 'uwsgi')
        except:
            return False
