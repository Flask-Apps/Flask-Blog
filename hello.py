import os

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
# needed for the flask-wtf
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    name = StringField(
        "What is your name?",
        validators=[
            DataRequired(),
        ],
    )
    submit = SubmitField("Submit")


@app.route("/", methods=["GET", "POST"])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""
    return render_template("index.html", form=form,
                           name=name, current_time=datetime.utcnow())


@app.route("/user/<name>")
def user(name):
    comments = [
        "When the horizon is at the top it's interesting",
        "When the horizon is at the bottom it's interesting",
        "When the horizon is at the middle it's not interesting",
    ]
    return render_template("user.html",
                           name=name,
                           comments=comments)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
