# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.models import db
from app.routes import auth_routes, users_routes

def create_app(port=5000, debug=False):
    app = Flask(__name__)

    # Set configuration variables directly
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'dingiswayo_calendar_schedular'

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Initialize JWT
    jwt = JWTManager(app)

    # Enable CORS
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

    # Register authentication blueprint
    app.register_blueprint(auth_routes.bp, url_prefix='/auth')
    app.register_blueprint(users_routes.users_bp, url_prefix='/users')

    # Run the Flask app with specified port and debug mode
    app.run(debug=debug, port=port)

    return app
