from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import User, Event, Attendee, CalendarShare, db
import bcrypt
from validation import is_valid_email, is_valid_password


# Creating Flask app and configuring JWT secret key
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'dingiswayo_calendar_schedular'  
api = Api(app)
jwt = JWTManager(app)

migrate = Migrate(app, db)
db.init_app(app)

with app.app_context():
    db.create_all()


############################### Authentification ###########################################################################
# Move the definition of the parser object to a global scope
parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=False, help='name is required')
parser.add_argument('email', type=str, required=True, help='Email is required')
parser.add_argument('password', type=str, required=True, help='Password is required')



# Resource for user login
class Login(Resource):
    def post(self):
        data = parser.parse_args()  # Use the global parser object for login
        email = data['email']
        password = data['password']

        user = User.query.filter_by(email=email).first()  # Querying user by email

        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password):
            return make_response(jsonify({'message': 'Invalid email or password'}), 401)  # Returning unauthorized access if email or password is incorrect

        access_token = create_access_token(identity=email)  # Creating access token for the user
        return make_response(jsonify({'access_token': access_token}), 200)  # Returning success response with access token

# Resource for user sign up
class SignUp(Resource):
    def post(self):
        data = parser.parse_args()  # Use the global parser object for sign-up
        name = data['name']
        email = data['email']
        password = data['password']

        user = User.query.filter_by(email=email).first()  # Querying user by email

        if not is_valid_email(email):
            return make_response(jsonify({'message': 'Invalid email address'}), 400)
        
        if user:
            return make_response(jsonify({'message': 'User already exists'}), 400)  # Returning bad request if user already exists
        
        if not is_valid_password(password):
            return make_response(jsonify({'message': 'Invalid password'}), 400)
            

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())  # Hashing password

        new_user = User(name=name, email=email, password=hashed_password)  # Creating new user with hashed password
        db.session.add(new_user)  # Adding user to the database session
        db.session.commit()  # Committing user to the database

        return make_response(jsonify({'message': 'User created successfully'}), 201)  # Returning success response with created user message


# Resource for user logout
class Logout(Resource):
    @jwt_required() # Requiring access token for this resource
    def post(self):
        email = get_jwt_identity() # Getting user email from access token
        return make_response(jsonify({'message': 'Logged out successfully'}), 200) # Returning success response with logged out message


##################################################################################################

#####################################Profile endpoints#########################################################

class UserInfo(Resource):
    def get(self, user_id):
        # Query user information
        user = User.query.get(user_id)

        if user is None:
            return {'message': 'User not found'}, 404

        # Serialize user object
        serialized_user = user.to_dict()

        # Construct the response dictionary
        response = {
            'name': serialized_user.get('name'),
            'email': serialized_user.get('email'),
            'image': serialized_user.get('image'),
            'phone_number': serialized_user.get('phone_number'),
            'profession': serialized_user.get('profession'),
            'about': serialized_user.get('about')
        }

        return response, 200



class EditUser(Resource):
    def patch(self, user_id):
        # Query user information
        user = User.query.get(user_id)
        
        if user is None:
            return {'message': 'User not found'}, 404

        # Update user attributes based on request data
        data = request.json  # Assuming JSON data is sent in the request
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        if 'image' in data:
            user.image = data['image']
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        if 'profession' in data:
            user.profession = data['profession']
        if 'about' in data:
            user.about = data['about']
        
        # Commit the changes to the database
        db.session.commit()

        # Return a success message
        return {'message': 'User updated successfully'}, 200

class DeleteUser(Resource):
    def delete(self, user_id):
        # Query the user by user_id
        user = User.query.get(user_id)
        
        # Check if the user exists
        if user is None:
            return {'message': 'User not found'}, 404
        
        # Delete the user from the database
        db.session.delete(user)
        db.session.commit()
        
        # Return a success message
        return {'message': 'User deleted successfully'}, 200

#########################################################################################################################
# Error handling for 404 - Not Found
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

# Error handling for 400 - Bad Request
@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

# Error handling for 401 - Unauthorized
@app.errorhandler(401)
def unauthorized(error):
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

# Adding resources to the API
api.add_resource(Login, '/login')
api.add_resource(SignUp, '/signup')
api.add_resource(Logout, '/logout')
api.add_resource(UserInfo, '/user/<int:user_id>')
api.add_resource(EditUser, '/edit_user/<int:user_id>')
api.add_resource(DeleteUser, '/delete_user/<ini:user_id>')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5555)