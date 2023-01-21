
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