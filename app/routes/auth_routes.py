# app/routes/auth_routes.py
from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from ..models import User  # Import the User model
from ..validation import is_valid_email, is_valid_password
from .. import db  # Import the db instance
import bcrypt

# Create a Blueprint for authentication routes
bp = Blueprint('auth', __name__)

# Create an instance of Api
api = Api(bp)

# Define a parser for request data
parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=False, help='name is required')
parser.add_argument('email', type=str, required=True, help='Email is required')
parser.add_argument('password', type=str, required=True, help='Password is required')
parser.add_argument('image', type=str, required=False)
parser.add_argument('phone_number', type=int, required=False)
parser.add_argument('profession', type=str, required=False)
parser.add_argument('about', type=str, required=False)

class SignUp(Resource):
    def post(self):
        data = parser.parse_args()  # Parse request data
        
        # Extract data from request
        name = data['name']
        email = data['email']
        password = data['password']

        # Check if the email is already registered
        if User.query.filter_by(email=email).first():
            return make_response(jsonify({'message': 'Email already registered'}), 400)

        # Validate email format
        if not is_valid_email(email):
            return make_response(jsonify({'message': 'Invalid email address'}), 400)

        # Validate password format
        if not is_valid_password(password, email):
            # Password is invalid
            return {'message': 'Passwords Cannot be an email'}, 400

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Create a new user object
        new_user = User(name=name, email=email, password=hashed_password)

        # Add the user to the database session
        db.session.add(new_user)
        
        try:
            # Commit the user to the database
            db.session.commit()
            return make_response(jsonify({'message': 'User created successfully'}), 201)
        except Exception as e:
            # Rollback in case of any error
            db.session.rollback()
            return make_response(jsonify({'message': str(e)}), 500)  # Internal Server Error

# Add the resource to the Api
api.add_resource(SignUp, '/signup')

# Resource for user login
class Login(Resource):
    def post(self):
        data = parser.parse_args()  # Use the global parser object for login
        email = data['email']
        password = data['password']

        user = User.query.filter_by(email=email).first()  # Querying user by email

        if not user or not isinstance(user.password, bytes):
            return make_response(jsonify({'message': 'Invalid email or password'}), 401)

        # Ensure user.password is of type bytes
        if not bcrypt.checkpw(password.encode('utf-8'), user.password):
            return make_response(jsonify({'message': 'Invalid email or password'}), 401)

        access_token = create_access_token(identity=user.id)  # Creating access token for the user's ID
        return make_response(jsonify({'access_token': access_token}), 200)  # Returning success response with access token

# Add the resource to the Api
api.add_resource(Login, '/login')

# Resource for user logout
class Logout(Resource):
    @jwt_required() # Requiring access token for this resource
    def post(self):
        email = get_jwt_identity() # Getting user email from access token
        # Perform any additional logout actions here if needed
        return make_response(jsonify({'message': 'Logged out successfully'}), 200) # Returning success response with logged out message

# Add the resource to the Api
api.add_resource(Logout, '/logout')


# Define a parser for request data
password_parser = reqparse.RequestParser()
password_parser.add_argument('email', type=str, required=True, help='Email is required')
password_parser.add_argument('new_password', type=str, required=True, help='New password is required')
password_parser.add_argument('confirm_new_password', type=str, required=True, help='Confirmation of new password is required')

class UpdatePassword(Resource):
    def patch(self):
        # Parse the request data
        data = password_parser.parse_args()
        
        # Extract data from request
        email = data['email']
        new_password = data['new_password']
        confirm_new_password = data['confirm_new_password']
        
        # Validate request data
        if not email or not new_password or not confirm_new_password:
            return {'message': 'Incomplete request data'}, 400
        
        # Validate email format
        if not is_valid_email(email):
            return {'message': 'Invalid email format'}, 400
        
        # Validate password format
        if not is_valid_password(new_password, email):
            # Password is invalid
            return {'message': 'Passwords Cannot be an email'}, 400
        # Check if passwords match
        if new_password != confirm_new_password:
            return {'message': 'Passwords do not match'}, 400
        
        # Query user by email
        user = User.query.filter_by(email=email).first()
        if not user:
            return {'message': 'User not found'}, 404
        
        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        # Update user's password with the hashed password
        user.password = hashed_password
        
        # Commit changes to the database
        db.session.commit()
        
        return {'message': 'Password updated successfully'}, 200
    
# Add the resource to the Api
api.add_resource(UpdatePassword, '/update_password')

