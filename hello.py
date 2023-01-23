import os

from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)


db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
# adds flask db command with several subcommands
migrate = Migrate(app, db)
mail = Mail(app)


# adding objects to the import list
# they will be available on the flask shell, no explicit imports needed
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


if __name__ == "__main__":
    app.run(debug=True)
