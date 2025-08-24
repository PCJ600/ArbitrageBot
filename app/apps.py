import os
import sys
import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        if self._should_load_cronjobs():
            try:
                from app.crons.cronjobs import register_cronjobs
                register_cronjobs()
                logger.info("Cronjobs loaded (PID: %s)", os.getpid())
            except Exception as e:
                logger.critical("Cronjob failed: %s", str(e))

    def _should_load_cronjobs(self):
        if any(cmd in sys.argv for cmd in ('test', 'migrate', 'makemigrations')):
            return False
        if 'runserver' in sys.argv:
            return os.environ.get('RUN_MAIN') == 'true'

        # prod env
        try:
            import psutil
            parent_name = psutil.Process(os.getppid()).name().lower()
            return 'gunicorn' in parent_name
        except Exception as e:
            logger.warning("Process detection failed: %s", str(e))
            return False
