from datetime import datetime
from flask import render_template, session, redirect, url_for, flash
from flask_login import login_required, current_user
from .forms import NameForm, EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import User, Role
from . import main
from ..decorators import admin_required


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


@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user.html", user=user)


@main.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash("Your profile has been updated.")
        return redirect(url_for(".user", username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", form=form)


@main.route("/edit-profile/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    # our form constructor requires user obj
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        # the data contains the id
        # query to load the role object by its id
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash("The profile has been updated.")
        return redirect(url_for(".user", username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    # we provide the role id here
    # list of tuples set in the choices attribute uses the
    # numeric identifiers to reference each option
    # coerce ensure the data attribute is always converted to int
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template("edit_profile.html", form=form, user=user)


# @main.route("/user/<name>")
# def user(name):
#     comments = [
#         "When the horizon is at the top it's interesting",
#         "When the horizon is at the bottom it's interesting",
#         "When the horizon is at the middle it's not interesting",
#     ]
#     return render_template("user.html", name=name, comments=comments)
