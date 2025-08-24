# ArbitrageBot

# Requirements
* RHEL 9.0/Debian 12 x86_64
* Python 3.9
* Django
* MySQL 8.0

# How To Start

## Configure your pushplus token on Host

Edit file /config.ini
```
[DEFAULT]
token = 12**2b
```
More details refer to [https://www.pushplus.plus/doc/](https://www.pushplus.plus/doc/)

## Configure your holdings in `qdii.py` and `ashare_lof.py`

```
HOLDING_FUNDS = {'501302', '160924'}
```

## Run on Host

```
# Install dependencies
rpm -i deps/mysql84-community-release-el8-2.noarch.rpm
dnf install -y python3-devel mysql-devel
pip3 install -r requirements.txt

# Make migrations
python3 manage.py makemigrations
python3 manage.py migrate

# Run in Host (dev)
python3 manage.py runserver localhost:8000

# Run in Host (prod)
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 proj.wsgi:application # foreground, for dev/test
gunicorn --bind 0.0.0.0:8000 --workers 2 --daemon proj.wsgi:application # background, for prod

# Use systemd
cp conf/arbitrage_bot.service /usr/lib/systemd/system/
systemctl start arbitrage_bot.service
systemctl enable arbitrage_bot.service
```

## Run in Docker

```
# Build image
./docker-build.sh

# Grant docker subnet access to database, for example
CREATE USER 'root'@'172.18.%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON your_database.* TO 'root'@'172.18.%';
FLUSH PRIVILEGES;

# Run in Docker
cd manifest/deploy/
docker compose up -d # Run
docker compose down # Stop
```

## run testcases

```
python3 manage.py test # Run all testcases.
python manage.py test app.tests.FundsNotifyTestCase # Run single testcase.
```
