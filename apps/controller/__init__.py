from flask import Blueprint

blueprint = Blueprint(
    'controller_blueprint',
    __name__,
    url_prefix=''
)