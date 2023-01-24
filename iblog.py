import os
from app import create_app, db
from app.models import User, Role
from flask_migrate import Migrate


app = create_app(os.getenv("FLASK_CONFIG", "default"))
# adds flask db command with several subcommands
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    """
    adding objects to the import list
    they will be available on the flask shell, no explicit imports needed
    """
    return dict(db=db, User=User, Role=Role)
