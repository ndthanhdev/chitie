# hola
Quản lý chi tiêu

# Setup

## Init project
1. Create local config file
```
$ cp config.py.example config.py
```

2. Create virtual environment
```
$ python3 -m venv env
$ souce env/bin/activate # Enter virtualenv
```

3. Install dependencies
```
$ pip install -e .
```

Install with dev tools `rich` `alembic`
```
$ pip install -e ".[dev]"
```

## For development
```
$ source FLASK_APP=api
$ flask run
```

## For production
Use uWSGI for web server with Nginx proxy
```
$ env/bin/uwsgi --enable-threads --socket 0.0.0.0:5000 --protocol http -w wsgi:hola_api
```

# Migration
Use [Alembic](https://alembic.sqlalchemy.org/en/latest/)
Create new migration
```
alembic revision -m "<migration_name>"
```

Upgrade
```
alembic upgrade +1
```

Downgrade
```
alembic downgrade -1
```