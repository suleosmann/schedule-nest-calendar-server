from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta  # Import timedelta for setting token expiry
from app.models import db
from app.routes import auth_routes, users_routes, events_routes, calendarshare_routes, attendees_routes
#from dateutil.rrule import InvalidRRuleError

# Inside your create_app function or wherever you initialize your Flask app
def create_app(port=5000, debug=False):
    app = Flask(__name__)

    # Set configuration variables directly
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'dingiswayo_calendar_schedular'
    
    # Set the default expiry of the access token to one hour
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Initialize JWT
    jwt = JWTManager(app)

    # Enable CORS and allow credentials
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)
    
    # Register authentication blueprint
    app.register_blueprint(auth_routes.bp, url_prefix='/auth')
    app.register_blueprint(users_routes.users_bp, url_prefix='/users')
    app.register_blueprint(events_routes.events_bp, url_prefix='/events')
    app.register_blueprint(calendarshare_routes.calendarshare_bp, url_prefix='/calendar')
    app.register_blueprint(attendees_routes.attendees_bp, url_prefix='/attendees')

    # Run the Flask app with specified port and debug mode
    app.run(debug=debug, port=port)
    
    return app