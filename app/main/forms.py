from wtforms import (
    StringField,
    SubmitField,
    TextAreaField,
    BooleanField,
    SelectField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    Regexp,
    ValidationError,
)
from flask_wtf import FlaskForm
from ..models import Role, User
from flask_pagedown.fields import PageDownField


class NameForm(FlaskForm):
    name = StringField(
        "What is your name?",
        validators=[
            DataRequired(),
        ],
    )
    submit = SubmitField("Submit")


class EditProfileForm(FlaskForm):
    name = StringField("Real Name", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0, 64)])
    about_me = TextAreaField("About Me")
    submit = SubmitField("Submit")


class EditProfileAdminForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(0, 64), Email()])
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,  # no special behaviour or options are being set
                # like re.IGNORECASE, re.MULTILINE, etc
                "Usernames must have only letters, numbers, dots or" "underscores",
            ),
        ],
    )
    confirmed = BooleanField("Confirmed")
    # coerce convert the user i/p (str) to int
    # user selected value will be converted to int
    # identifier for each role is set to id of each role (int)
    # since we use coerce=int so field values are stored as integers
    # instead of he default(str)
    # form.role.data = 1
    role = SelectField("Role", coerce=int)
    name = StringField("Real Name", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0, 64)])
    about_me = TextAreaField("About Me")
    submit = SubmitField("Submit")

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [
            (role.id, role.name) for role in Role.query.order_by(Role.name).all()
        ]
        # for the validation we'll need this
        self.user = user

    def validate_email(self, field):
        if (
            field.data != self.user.email
            and User.query.filter_by(email=field.data).first()
        ):
            raise ValidationError("Email already registered.")

    def validate_username(self, field):
        if (
            field.data != self.user.username
            and User.query.filter_by(username=field.data).first()
        ):
            raise ValidationError("Username already in use.")


class PostForm(FlaskForm):
    # body = TextAreaField("What's on your mind?", validators=[DataRequired()])
    # client-side Markdown-to-HTML converter implemented in js
    body = PageDownField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField("Submit")


class CommentForm(FlaskForm):
    body = StringField("", validators=[DataRequired()])
    submit = SubmitField("Submit")
