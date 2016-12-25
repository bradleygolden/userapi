# userapi

userapi is a simple Flask api for managing users. It's meant to be small and lightweight.

The default database for production is postgres but you can very easily change that in the config.py file yourself by changing the ```SQLALCHEMY_DATABASE_URI``` value.

## Setup

#### Set environment variables
```
$ export FLASK_ENV=dev|qa|prod
$ export FLASK_APP=$(pwd)/app.py
```

#### Install dependencies from PIP
```
$ pip install -r requirements.txt
```

#### Prod
```
# create postgres database named 'userapi'
$ pip install psycopg2 (or other db driver)
$ flask db init
$ flask db migrate
$ flask db upgrade
```

## Run

#### Development
```
$ python app.py
```

#### QA
```
$ python app.py
```

#### Prod
```
$ gunicorn --bind <ip>:<port> wsgi
```
