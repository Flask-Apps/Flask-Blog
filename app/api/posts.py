from flask import request, g, jsonify, url_for, current_app

from . import api
from ..models import Post, Permission
from .. import db
from .errors import forbidden
from .decorators import permission_required


@api.route("/posts/")
def get_posts():
    page = request.args.get("page", 1, type=int)
    pagination = Post.query.paginate(
        page=page, per_page=current_app.config["IBLOG_POSTS_PER_PAGE"], error_out=False
    )
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for(".get_posts", page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for(".get_posts", page=page + 1)
    return jsonify(
        {
            "posts": [post.to_json() for post in posts],
            "prev_url": prev,
            "next_url": next,
            "count": pagination.total,
        }
    )


@api.route("/posts/<int:id>")
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


@api.route("/posts/", methods=["POST"])
@permission_required(Permission.WRITE)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return (
        jsonify(post.to_json()),
        201,
        # added a location header
        {"Location": url_for("api.get_post", id=post.id)},
    )


@api.route("/posts/<int:id>", methods=["PUT"])
@permission_required(Permission.WRITE)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and not g.current_user.can(Permission.ADMIN):
        return forbidden("Insufficient Permissions")
    post.body = request.json.get("body", post.body)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())
