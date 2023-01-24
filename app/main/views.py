from datetime import datetime
from flask import render_template, session, redirect, url_for, flash
from . import main
from .forms import NameForm
from .. import db
from ..models import User


@main.route("/", methods=["GET", "POST"])
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
            # if admin := app.config["IBLOG_ADMIN"]:
            #     send_email(admin, "New User", "mail/new_user", user=user)
        else:
            session["known"] = True
            flash("We already know you!")
        session["name"] = form.name.data
        form.name.data = ""
        # status 302 redirect
        # endpoint name is view function attached
        # namespace.endpoint, here main.index
        # or .index blueprint name for the current request is used to
        # complete the endpoint name
        return redirect(url_for(".index"))
    return render_template(
        "index.html",
        form=form,
        name=session.get("name"),
        current_time=datetime.utcnow(),
        known=session.get("known", False),
    )


@main.route("/user/<name>")
def user(name):
    comments = [
        "When the horizon is at the top it's interesting",
        "When the horizon is at the bottom it's interesting",
        "When the horizon is at the middle it's not interesting",
    ]
    return render_template("user.html", name=name, comments=comments)
