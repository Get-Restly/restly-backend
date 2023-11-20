from flask import Blueprint
from .health import health_bp
from .spec import spec_bp
from .tutorial import tutorial_bp


routes_bp = Blueprint("routes", __name__)

routes_bp.register_blueprint(health_bp)
routes_bp.register_blueprint(spec_bp)
routes_bp.register_blueprint(tutorial_bp)
