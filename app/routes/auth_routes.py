# app/routes/auth_routes.py
from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from ..models import User
from ..validation import is_valid_email, is_valid_password
from .. import db
import bcrypt

# Create a Blueprint for authentication routes
bp = Blueprint('auth', __name__)
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

# Define the update_password_parser directly in auth_routes.py
update_password_parser = reqparse.RequestParser()
update_password_parser.add_argument('email', type=str, required=True, help='Email is required')
update_password_parser.add_argument('new_password', type=str, required=True, help='New Password is required')
update_password_parser.add_argument('confirm_new_password', type=str, required=True, help='Confirmation of new password is required')

# Resource for user registration
class SignUp(Resource):
    def post(self):
        data = parser.parse_args()  # Parse request data
        name = data['name']
        email = data['email']
        password = data['password']

        if User.query.filter_by(email=email).first():
            return make_response(jsonify({'message': 'Email already registered'}), 400)

        if not is_valid_email(email):
            return make_response(jsonify({'message': 'Invalid email address'}), 400)

        if not is_valid_password(password, email):
            return {'message': 'Passwords Cannot be an email'}, 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        
        try:
            db.session.commit()
            return make_response(jsonify({'message': 'User created successfully'}), 201)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': str(e)}), 500)

# Add the resource to the Api
api.add_resource(SignUp, '/signup')

# Resource for user login
class Login(Resource):
    def post(self):
        data = parser.parse_args()
        email = data['email']
        password = data['password']

        user = User.query.filter_by(email=email).first()

        if not user or not isinstance(user.password, bytes):
            return make_response(jsonify({'message': 'Invalid email or password'}), 401)

        if not bcrypt.checkpw(password.encode('utf-8'), user.password):
            return make_response(jsonify({'message': 'Invalid email or password'}), 401)

        access_token = create_access_token(identity=user.id)
        return make_response(jsonify({'access_token': access_token}), 200)

# Add the resource to the Api
api.add_resource(Login, '/login')

# Resource for user logout
class Logout(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        return make_response(jsonify({'message': 'Logged out successfully'}), 200)

# Add the resource to the Api
api.add_resource(Logout, '/logout')

# Resource for changing user password
class UpdatePassword(Resource):
    def patch(self):
        data = update_password_parser.parse_args()
        email = data['email']
        new_password = data['new_password']
        confirm_new_password = data['confirm_new_password']

        if not email or not new_password or not confirm_new_password:
            return {'message': 'Incomplete request data'}, 400

        if not is_valid_email(email):
            return {'message': 'Invalid email format'}, 400

        if not is_valid_password(new_password, email):
            return {'message': 'Invalid password format'}, 400

        if new_password != confirm_new_password:
            return {'message': 'Passwords do not match'}, 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return {'message': 'User not found'}, 404

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.password = hashed_password
        db.session.commit()

        return {'message': 'Password updated successfully'}, 200

# Add the resource to the Api
api.add_resource(UpdatePassword, '/update_password')
