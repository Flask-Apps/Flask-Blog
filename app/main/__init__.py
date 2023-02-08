from flask import Blueprint
from ..models import Permission

main = Blueprint("main", __name__)

# modules imported at the bottom to avoid errors due to
# circular dependencies
# the views and erros are going to import main blueprint object
# so the imports are going to fail unless the circular reference
# occurs after main is defined


@main.app_context_processor
def inject_permissions():
    # now the Permission object can be accessed from templates
    # during rendering
    return dict(Permission=Permission)


from . import views, errors  # noqa
