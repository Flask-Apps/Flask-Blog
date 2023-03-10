from iblog import db
from iblog import Role, User, app


def fix_role_permission_to_ones_lacking():
    # Update the user list so that all the user accounts that were create
    # b4 adding roles and permission existed have a role assigned
    admin_role = Role.query.filter_by(name="Administrator").first()
    default_role = Role.query.filter_by(default=True).first()
    for u in User.query.all():
        if u.role is None:
            if u.email == app.config["IBLOG_ADMIN"]:
                u.role = admin_role
            else:
                u.role = default_role
    db.session.commit()


with app.app_context():
    # brute force: remove the old tables
    db.drop_all()
    # create all model tables subclass of db.Model
    db.create_all()

    Role.insert_roles()
    fix_role_permission_to_ones_lacking()

    # add to roles table using Role model
    # admin_role = Role(name="Admin")
    # mod_role = Role(name="Moderator")
    # user_role = Role(name="User")

    # # add to users table using User model
    # # role is available as it's a high level representation of
    # # the one-to-many relationship
    # user_john = User(username="john", email="john@gmail.com",
    #                  role=admin_role)
    # user_susan = User(username="susan", email="susan@gmail.com",
    #                   role=user_role)
    # user_david = User(username="david", email="david@gmail.com",
    #                   role=user_role)

    # # object only exist in python side so no id at first
    # print("before commit: ", admin_role.id)

    # # prepare objects to be written to the database
    # # db.session.add(admin_role)
    # # db.session.add(user_role)
    # # db.session.add(mod_role)
    # # db.session.add(user_john)
    # # db.session.add(user_susan)
    # # db.session.add(user_david)
    # try:
    #     db.session.add_all(
    #         [admin_role, mod_role, user_role, user_john, user_susan,
    #          user_david]
    #     )
    # except Exception as err:
    #     print(err, type(err))
    #     # db sessions are also called transactions
    #     # if error occurs during any transactions
    #     # we can roll back or restore to the state they have in the db
    #     db.session.rollback()
    # # write objects to the database
    # db.session.commit()

    # print("after commit: ", admin_role.id)

    # # just for information

    # def modify_row():
    #     admin_role.name = "Administrato"
    #     db.session.add(admin_role)
    #     db.session.commit()

    # def delete_row():
    #     db.session.delete(mod_role)
    #     db.session.commit()

    # def get_object_from_database():
    #     user_role = Role.query.filter_by(name="User").first()
    #     return user_role

    # def get_users_from_role():
    #     # we can apply filter because we have used lazy="dynamic"
    #     # this won't execute the query right away so we can
    #     # add to the query
    #     print(user_role.users.order_by(User.username).all())
    #     print(user_role.users.order_by(User.username).count())
