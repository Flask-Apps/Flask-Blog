from flask import Blueprint

main = Blueprint("main", __name__)

# modules imported at the bottom to avoid errors due to
# circular dependencies
# the views and erros are going to import main blueprint object
# so the imports are going to fail unless the circular reference
# occurs after main is defined
from . import views, errors
