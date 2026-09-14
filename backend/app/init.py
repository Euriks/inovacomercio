from __future__ import annotations
from flask import Flask, jsonify
from flask_cors import CORS
from app.config import get_settings
from app.extensions import db, jwt, migrate

def create_app() -> Flask:
    app = Flask(__name__)
    settings = get_settings()

    app.config["SECRET_KEY"] = settings.secret_key
    app.config["JWT_SECRET_KEY"] = settings.jwt_secret_key
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.database_uri

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    @app.route("/api/v1/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "healthy", "env": settings.env}), 200

    return app