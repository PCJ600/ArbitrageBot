# ArbitrageBot

# Requirements
RHEL 9.0
MySQL
Django

# Configure
```
/usr/AB/config.ini 配置token
```

# How To Start
```
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```

# TODO
* 从集思录获取T+0 美股+大宗商品QDII
* 每天通知次数限制, 通知失败记录日志
