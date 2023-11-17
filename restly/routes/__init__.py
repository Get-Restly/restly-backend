from flask import Blueprint
from .health import health_bp


routes_bp = Blueprint("routes", __name__)

routes_bp.register_blueprint(health_bp)
