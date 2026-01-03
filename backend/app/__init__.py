from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import db, jwt

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)

    from .routes.auth import auth_bp
    from .routes.trip import trip_bp
    from .routes.activity import activity_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(trip_bp, url_prefix="/api/trips")
    app.register_blueprint(activity_bp, url_prefix="/api/activities")

    with app.app_context():
        db.create_all()

    return app
