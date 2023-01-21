import os

from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from datetime import datetime
from dotenv import load_dotenv
from threading import Thread

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# needed for the flask-wtf
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "data.sqlite"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["IBLOG_MAIL_SUBJECT_PREFIX"] = "[IBlog]"
app.config["IBLOG_MAIL_SENDER"] = "IBlog Admin <admin@iblog.com>"
app.config["IBLOG_ADMIN"] = os.environ.get("IBLOG_ADMIN")


db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
# adds flask db command with several subcommands
migrate = Migrate(app, db)
mail = Mail(app)


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    # representing one to many
    # a new column called role will be introduced in users table
    users = db.relationship("User", backref="role", lazy="dynamic")

    def __repr__(self):
        return "<Role %r>" % self.name

    def __str__(self):
        return self.name


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    # we can also define many to one like this:
    # a new column called users will be introduced in Role model
    # role = db.relationship("Role", backref="users")

    def __repr__(self):
        return "<User %r>" % self.username

    def __str__(self):
        return self.username


class NameForm(FlaskForm):
    name = StringField(
        "What is your name?",
        validators=[
            DataRequired(),
        ],
    )
    submit = SubmitField("Submit")


def send_async_email(app, msg):
    # needs the application context to be created artificially
    # contexts are associated with a thread when mail.send() executes
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(
        app.config["IBLOG_MAIL_SUBJECT_PREFIX"] + subject,
        sender=app.config["IBLOG_MAIL_SENDER"],
        recipients=[to],
    )
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    # moving email sending function to a background thread
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


# adding objects to the import list
# they will be available on the flask shell, no explicit imports needed
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.route("/", methods=["GET", "POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        # POST, REDIRECT AND GET
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session["known"] = False
            flash("Looks like you have changed your name!")
            if admin := app.config["IBLOG_ADMIN"]:
                send_email(admin, "New User", "mail/new_user", user=user)
        else:
            session["known"] = True
            flash("We already know you!")
        session["name"] = form.name.data
        form.name.data = ""
        # status 302 redirect
        # endpoint name is view function attached
        return redirect(url_for("index"))
    return render_template(
        "index.html",
        form=form,
        name=session.get("name"),
        current_time=datetime.utcnow(),
        known=session.get("known", False),
    )


@app.route("/user/<name>")
def user(name):
    comments = [
        "When the horizon is at the top it's interesting",
        "When the horizon is at the bottom it's interesting",
        "When the horizon is at the middle it's not interesting",
    ]
    return render_template("user.html", name=name, comments=comments)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
