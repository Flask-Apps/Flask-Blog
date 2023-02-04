import os

from flask import (
    current_user,
    render_template,
    redirect,
    request,
    url_for,
    flash,
)  # noqa
from flask_login import login_user, logout_user, login_required
from . import auth
from .. import db
from ..email import send_email
from ..models import User
from .forms import LoginForm, RegistrationForm
from dotenv import load_dotenv

load_dotenv()


@auth.before_app_request
def before_request():
    if (
        current_user.is_authenticated
        and not current_user.confirmed
        and request.blueprint != "auth"
        and request.endpoint != "static"
    ):
        return redirect(url_for("auth.unconfirmed"))


@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")


@auth.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(
        current_user.email,
        "Confirm Your Account",
        "auth/email/confirm",
        user=current_user,
        token=token,
    )
    flash("A new confirmation email has been sent to you by email")
    return redirect(url_for("main.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
        )
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(
            user.email,
            "Confirm You Account",
            "auth/email/confirm",
            user=user,
            token=token,
        )
        flash("A confirmation email has been sent to you by email.")
        return redirect(url_for("main.index"))
        # return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(
        token, expiration=os.getenv("TOKEN_EXPIRE_TIME", 3600)
    ):  # noqa
        db.session.commit()
    else:
        flash("The confirmation link is invalid or has expired.")
    return redirect(url_for("main.index"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            # writes the ID of the user to the user session as a string
            login_user(user, form.remember_me.data)
            next = request.args.get("next")
            if next is None or not next.startswith("/"):
                next = url_for("main.index")
            return redirect(next)
        flash("Invalid username or password")
    return render_template("auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    # remove and reset the user session
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("main.index"))
