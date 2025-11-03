from flask import Blueprint

bp = Blueprint('designer', __name__)

from app.designer import routes