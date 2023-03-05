import os
import sys
import click
from app import create_app, db
from app.models import User, Role, Post
from flask_migrate import Migrate
from flask_login import login_required
from dotenv import load_dotenv

load_dotenv()


app = create_app(os.getenv("FLASK_CONFIG", "default"))
COV = None
if os.environ.get("IBLOG_COVERAGE"):
    import coverage

    COV = coverage.coverage(branch=True, include="app/*")
    COV.start()

# adds flask db command with several subcommands
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    """
    adding objects to the import list
    they will be available on the flask shell, no explicit imports needed
    """
    return dict(db=db, User=User, Role=Role, Post=Post)


# @app.cli.command()
# def test():
#     """Run the unit tests."""
#     import unittest

#     tests = unittest.TestLoader().discover("tests")
#     unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
@click.option(
    "--coverage/--no-coverage", default=False, help="Run tests under code coverage"
)
def test(coverage):
    """Run the unit tests."""
    if coverage and not os.environ.get("IBLOG_COVERAGE"):
        os.environ["IBLOG_COVERAGE"] = "1"
        # restart the script with new option
        os.execv(sys.executable, [sys.executable] + sys.argv)
    import unittest

    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print("Coverage Summary:")
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, "tmp/coverage")
        COV.html_report(directory=covdir)
        print("HTML version: file://%s/index.html" % covdir)
        COV.erase()


@app.route("/secret")
@login_required
def secret():
    """If the user is not authenticated flask_login will
    intercept the request and send the user to the login page
    """
    return "Only authenticated users are allowed!"


if __name__ == "__main__":
    app.run("0.0.0.0")
