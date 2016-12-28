# userapi

[![Build Status](https://travis-ci.org/bradleygolden/userapi.svg?branch=master)](https://travis-ci.org/bradleygolden/userapi)
[![Coverage Status](https://coveralls.io/repos/github/bradleygolden/userapi/badge.svg?branch=master)](https://coveralls.io/github/bradleygolden/userapi?branch=master)

userapi is a simple Flask api for managing users. It's meant to be small and lightweight.

The default database for production is postgres but you can very easily change that in the config.py file yourself by changing the ```SQLALCHEMY_DATABASE_URI``` value to a [valid connection string](http://docs.sqlalchemy.org/en/latest/core/engines.html).

## Setup

#### Set environment variables
```
$ export FLASK_ENV=dev|test|prod
$ export FLASK_APP=$(pwd)/app.py
```

#### Install dependencies via pip
```
$ pip install -r requirements.txt
```

#### Setup database
Note: If FLASK_ENV is set to dev or test, you can ignore this step. SQLite is used by default.
```
# install database dependencies
$ pip install psycopg2

# create a postgres database named 'userapi'
```

#### Perform database migrations
```
$ flask db init
$ flask db migrate
$ flask db upgrade
```

#### Create an api user
```
python -c "import app; app.create_user('username', 'password')"
```

## Run

#### Development
```
$ flask run
```

#### Prod
```
$ gunicorn --bind 0.0.0.0:8000 wsgi
```

## Testing

#### Install testing dependencies
```
$ pip install -r testrequirements.txt
```

#### Run tests and generate coverage report
```
$ py.test --cov-report=term-missing --cov=app tests/
```
