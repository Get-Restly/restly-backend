import os

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from .config import DevelopmentConfig, ProductionConfig
from .db import db
from .routes import routes_bp
from .models import User, Spec, Tutorial


def create_app():
    app = Flask(__name__)
    debug = os.environ.get("FLASK_DEBUG", 0)

    if debug:
        app.config.from_object(DevelopmentConfig)
        CORS(app)
    else:
        app.config.from_object(ProductionConfig)
        CORS(app)

    db.init_app(app)
    migrate = Migrate(app, db)
    app.register_blueprint(routes_bp)

    return app
