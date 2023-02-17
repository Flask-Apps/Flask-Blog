from flask import render_template, redirect, url_for, flash, current_app, request
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from .. import db
from ..models import User, Role, Permission, Post
from . import main
from ..decorators import admin_required


@main.route("/", methods=["GET", "POST"])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page,
        per_page=int(current_app.config["IBLOG_POSTS_PER_PAGE"]),
        error_out=False,
    )
    # posts = Post.query.order_by(Post.timestamp.desc()).all()
    posts = pagination.items
    return render_template("index.html", form=form, posts=posts, pagination=pagination)


@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template("user.html", user=user, posts=posts)


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
