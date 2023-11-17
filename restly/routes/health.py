from flask import Blueprint


health_bp = Blueprint("health", __name__)


@health_bp.route("/")
def health():
    return {"status": "OK"}
