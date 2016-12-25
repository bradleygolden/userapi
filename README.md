# userapi

userapi is a simple Flask server api for managing users. It's meant to be small and lightweight.

The database default for production is postgres but you can very easily change that in the config.py file yourself by changing the ```SQLALCHEMY_DATABASE_URI``` value.

## Setup

##### Set environment variables
```
$ export FLASK_ENV=dev|qa|prod
$ export FLASK_APP=$(pwd)/app.py
```

##### Prod
```
# create postgres database named 'userapi'
# pip install psycopg2
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
