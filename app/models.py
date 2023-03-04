import hashlib
import bleach

from markdown import markdown
from . import db, login_manager
from flask import current_app, url_for  # , request
from app.exceptions import ValidationError
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import datetime


class Permission:
    # Using power of 2 helps to keep each combination unique
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    # representing one to many
    # a new column called role will be introduced in users table
    users = db.relationship("User", backref="role", lazy="dynamic")
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        # sql alchemy will set the permissions field None by default
        # we use class constructor to set it to 0 if an initial value
        # isn't provided in the constructor arguments
        # This can be done easily by using default value though
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return "<Role %r>" % self.name

    def __str__(self):
        return self.name

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permission(self):
        self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            "User": [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            "Moderator": [
                Permission.FOLLOW,
                Permission.COMMENT,
                Permission.WRITE,
                Permission.MODERATE,
            ],
            "Administrator": [
                Permission.FOLLOW,
                Permission.COMMENT,
                Permission.WRITE,
                Permission.MODERATE,
                Permission.ADMIN,
            ],
        }
        default_role = "User"
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permission()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = role.name == default_role
            db.session.add(role)
        db.session.commit()


class Follow(db.Model):
    __tablename__ = "follows"
    # many to one using foreignkey
    follower_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    # we can also define many to one like this:
    # a new column called users will be introduced in Role model
    # role = db.relationship("Role", backref="users", lazy="dynamic")

    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    # for user profile
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    # caching the md5 hash to avoid frequent cpu intensive operation
    avatar_hash = db.Column(db.String(32))
    # one to many relationship User 1-n Post
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    comments = db.relationship("Comment", backref="author", lazy="dynamic")

    # follower
    followed = db.relationship(
        "Follow",
        foreign_keys=[Follow.follower_id],
        backref=db.backref(
            "follower",
            # when Follow object is queried,
            # its related object (i.e., the current object)
            # should be loaded in the same query
            lazy="joined",
        ),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    followers = db.relationship(
        "Follow",
        foreign_keys=[Follow.followed_id],
        backref=db.backref("followed", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs) -> None:
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config["IBLOG_ADMIN"]:
                self.role = Role.query.filter_by(name="Administrator").first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()
        self.follow(self)
        # if User.query.filter_by(email=self.email).first():

    def __repr__(self):
        return "<User %r>" % self.username

    def __str__(self):
        return self.username

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(
            Follow.follower_id == self.id
        )

    def generate_confirmation_token(self):
        s = Serializer(current_app.config["SECRET_KEY"])
        return s.dumps({"confirm": self.id})

    def confirm(self, token, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token, max_age=expiration)
        except:  # noqa
            return False

        if data.get("confirm") != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self):
        s = Serializer(current_app.config["SECRET_KEY"])
        return s.dumps({"reset": self.id})

    @staticmethod
    def reset_password(token, new_password, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token, max_age=expiration)
        except:  # noqa
            return False
        user = User.query.get(data.get("reset"))
        if user is None:
            return False
        # if data.get("reset") != user.id:
        #     return False
        user.password = new_password
        db.session.add(user)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def generate_email_change_token(self, new_email):
        s = Serializer(current_app.config["SECRET_KEY"])
        return s.dumps({"change_email": self.id, "new_email": new_email})

    def change_email(self, token, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token, max_age=expiration)
        except:  # noqa
            return False
        # this ensures that one person token can't be used to change email
        # of another user
        if data.get("change_email") != self.id:
            return False
        new_email = data.get("new_email")
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        # after email change create a new avatar hash
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)
        return True

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode("utf-8")).hexdigest()

    def gravatar(self, size=100, default="identicon", rating="g"):
        # if request.is_secure:
        #     url = "https://secure.gravatar.com/avatar"
        # else:
        #     url = "http://www.gravatar.com/avatar"
        url = "https://secure.gravatar.com/avatar"
        hash = self.avatar_hash or self.gravatar_hash()
        return f"{url}/{hash}?s={size}&d={default}&r={rating}"

    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        # for user who have not been commited to db
        if user.id is None:
            return False
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def generate_auth_token(self):
        s = Serializer(current_app.config["SECRET_KEY"])
        return s.dumps({"id": self.id})

    @staticmethod
    def verify_auth_token(token, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token, max_age=expiration)
        except:  # noqa
            return None
        return User.query.get(data["id"])

    def to_json(self):
        json_user = {
            "url": url_for("api.get_user", id=self.id),
            "username": self.username,
            "member_since": self.member_since,
            "last_seen": self.last_seen,
            "posts_url": url_for("api.get_user_posts", id=self.id),
            "followed_posts_url": url_for("api.get_user_followed_posts", id=self.id),
            "post_count": self.posts.count(),
        }
        return json_user


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey(User.id))
    # keeps the converted text, Markdown to HTML
    body_html = db.Column(db.Text)
    comments = db.relationship("Comment", backref="post", lazy="dynamic")

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        """
        Handles the conversion of Markdown text to HTML
        Steps:
        1) markdown() func does initial conversion to HTML
        2) result passed to clean(), along with the approved tags
            the clean func removes any tags not on the whitelist
        3) final conversion done with linkify(),
            converts any URLs written in plain text into proper <a> links
        - renders the html version of the body and stores
            it in body_html
        """
        allowed_tags = [
            "a",
            "abbr",
            "acronym",
            "b",
            "blockquote",
            "code",
            "em",
            "i",
            "li",
            "ol",
            "pre",
            "strong",
            "ul",
            "h1",
            "h2",
            "h3",
            "p",
        ]
        # sanitize to ensure only short list of HTML tags are allowed
        target.body_html = bleach.linkify(
            bleach.clean(
                # server side markdown to html converter
                markdown(value, output_format="html"),
                tags=allowed_tags,
                strip=True,
            )
        )

    def to_json(self):
        json_post = {
            "url": url_for("api.get_post", id=self.id),
            "body": self.body,
            "body_html": self.body_html,
            "timestamp": self.timestamp,
            "author_url": url_for("api.get_user", id=self.author_id),
            "comments_url": url_for("api.get_post_comments", id=self.id),
            "comment_count": self.comments.count(),
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get("body")
        if body is None or body == "":
            raise ValidationError("post does not have a body")
        # 1) server-side Markdown rendering is automatically triggered
        #   by an SQLAlchemy event whenever the body attribute is
        #   modified
        # 2) resource urls are defined by the server, not the client
        # 3) client has no authority to select the author of the blog
        #   post
        return Post(body=body)


# registering the on_changed_body as a listener of SQLAlchemy's
# "set" even for body
# invoke when the body field is set to a new value
db.event.listen(Post.body, "set", Post.on_changed_body)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permission):  # noqa
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    """Retrieve information about the logged-in user

    Args:
        user_id (str): user identifier

    Returns:
        - User: User object if valid OR,
        - None: User identifier is invalid or error occurred

    """
    return User.query.get(int(user_id))


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ["a", "abbr", "acronym", "b", "code", "em", "i", "strong"]
        target.body_html = bleach.linkify(
            bleach.clean(
                markdown(value, output_format="html"), tags=allowed_tags, strip=True
            )
        )

    def to_json(self):
        json_comment = {
            "url": url_for("api.get_comment", id=self.id),
            "post_url": url_for("api.get_post", id=self.post_id),
            "body": self.body,
            "body_html": self.body_html,
            "timestamp": self.timestamp,
            "author_url": url_for("api.get_user", id=self.author_id),
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get("body")
        if body is None or body == "":
            raise ValidationError("comment does not have a body")
        return Comment(body=body)


db.event.listen(Comment.body, "set", Comment.on_changed_body)
