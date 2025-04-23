# ArbitrageBot

# Requirements
RHEL 9.0
MySQL
Django

# How To Start
```
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```

# Next Step

定时从集思录获取数据 (保存到数据库 ?, 保留7天 ?)
通知条件(涨幅>5% && 溢价>5%, 考虑读不到数据的可能性)
基金分类(etf, lof, 港股, 美股, 大宗商品)

通知接口测试

通知次数限制(每天限制, 每个标的限制)
只在交易时间获取集思录数据 (登录问题?)
非交易时间删除历史数据
错误记录到日志
