# ArbitrageBot

# Requirements
* RHEL 9.0 x86_64
* MySQL 8.0
* Django

# How To Start

## configure your pushplus token
```
/usr/ArbitrageBot/config.ini
[DEFAULT]
token = 12**2b
```

## configure your holdings in `query_funds.py`

## run django project
```
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```

## auto-restart
```
cp conf/arbitrage_bot.service /usr/lib/systemd/system/
systemctl start arbitrage_bot.service
systemctl enable arbitrage_bot.service
```

# Doc
[https://www.pushplus.plus/doc/](https://www.pushplus.plus/doc/)
