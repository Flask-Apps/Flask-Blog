# Steps for heroku deployment (PaaS)

## Initial steps

- `heroku login`
- `heroku create iblog`: to register the application with heroku, name should be unique
  - heroku creates a Git server dedicated to our application
  - we can see it with `git remote show heroku`
- `heroku config:set FLASK_APP=iblog.py`: register env variable so that it is always set when heroku executes commands related to this application

## Provisioning a db

- `heroku addons:create heroku-postgresql:hobby-dev`: attach postgres db to our application
- we get the `DATABASE_URL` env variable and our application uses it if it's available

## Configuring Logging

- see `HerokuConfig`
- when application is executed by heroku, it needs to know that this new configuration needs to be used
    - `heroku config:set FLASK_CONFIG=heroku`