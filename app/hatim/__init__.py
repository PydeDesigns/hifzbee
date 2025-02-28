from flask import Blueprint

bp = Blueprint('hatim', __name__)

from app.hatim import routes
