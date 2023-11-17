from flask import Flask
from .config import DevelopmentConfig, ProductionConfig
from .routes import routes_bp
import os


def create_app():
    app = Flask(__name__)
    debug = os.environ.get("FLASK_DEBUG", 0)

    if debug:
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(ProductionConfig)

    app.register_blueprint(routes_bp)

    return app
