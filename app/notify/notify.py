import configparser
import logging
import os
import requests
import threading
import traceback

logger = logging.getLogger('app')

# refer to https://www.pushplus.plus
class NotifyHandler:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(NotifyHandler, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.token = None
        self.init_token()

    def init_token(self):
        config_file='/usr/ArbitrageBot/config.ini'
        if not os.path.exists(config_file):
            raise FileNotFoundError(f'config.ini not found')

        cfg = configparser.ConfigParser()
        cfg.read(config_file)

        try:
            self.token = cfg['DEFAULT']['token']
        except KeyError as e:
            raise ValueError('token not found in config.ini')


    def send_message(self, message):
        url = 'https://www.pushplus.plus/send'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        body = {
            "token": self.token,
            "title": message,
            "content": message
		}
        try:
            resp = requests.post(url, json=body, headers=headers, timeout=(10,30))
            if resp.status_code != 200:
                logger.error("send message failed, http_code: %r", resp.status_code)
                return

            resp_data = resp.json()
            resp_code = resp_data.get('code')
            logging.info("send message %r, resp_data: %r", message, resp_data)
        except Exception as e:
            logging.error("send message exception: %r, tb: %r", e, traceback.format_exc())


notify_handler = NotifyHandler()
