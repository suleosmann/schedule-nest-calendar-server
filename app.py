from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import User,db
import bcrypt

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'dingiswayo_calendar_schedular'  
api = Api(app)
jwt = JWTManager(app)


parser = reqparse.RequestParser()
parser.add_argument('email', type=str, required=True, help='Email is required')
parser.add_argument('password', type=str, required=True, help='Password is required')

class Login(Resource):
    def post(self):
        data = parser.parse_args()
        email = data['email']
        password = data['password']

        user = User.query.filter_by(email=email).first()

        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password):
            return make_response(jsonify({'message': 'Invalid email or password'}), 401)

        access_token = create_access_token(identity=email)
        return make_response(jsonify({'access_token': access_token}), 200)
    
class SignUp(Resource):
    def post(self):
        data = parser.parse_args()
        email = data['email']
        password = data['password']

        user = User.query.filter_by(email=email).first()

        if user:
            return make_response(jsonify({'message': 'User already exists'}), 400)

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return make_response(jsonify({'message': 'User created successfully'}), 201)
    

class Logout(Resource):
    @jwt_required()
    def post(self):
        email = get_jwt_identity()
        return make_response(jsonify({'message': 'Logged out successfully'}), 200)