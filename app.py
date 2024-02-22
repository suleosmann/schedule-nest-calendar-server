from asyncio import events
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import User, Event, Attendee, CalendarShare, db
import bcrypt
from validation import is_valid_email, is_valid_password, validate_phone_number
from flask_bcrypt import check_password_hash, generate_password_hash
from recurrence_helper import generate_recurrences
from datetime import datetime



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

from validation import is_valid_email, is_valid_password

class UpdatePassword(Resource):
    def patch(self):
        # Parse the request data
        data = request.json
        
        # Validate request data
        if 'email' not in data or 'new_password' not in data or 'confirm_new_password' not in data:
            return {'message': 'Incomplete request data'}, 400
        
        email = data['email']
        new_password = data['new_password']
        confirm_new_password = data['confirm_new_password']
        
        # Validate email format
        if not is_valid_email(email):
            return {'message': 'Invalid email format'}, 400
        
        # Validate password format
        if not is_valid_password(new_password):
            return {'message': 'Invalid password format'}, 400
        
        # Check if passwords match
        if new_password != confirm_new_password:
            return {'message': 'Passwords do not match'}, 400
        
        # Query user by email
        user = User.query.filter_by(email=email).first()
        if user is None:
            return {'message': 'User not found'}, 404
        
        # Update user's password
        user.password = generate_password_hash(new_password)
        
        # Commit changes to the database
        db.session.commit()
        
        return {'message': 'Password updated successfully'}, 200


##################################################################################################

#####################################Profile endpoints#########################################################

class UserInfo(Resource):
    @jwt_required()
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
    @jwt_required()
    def patch(self, user_id):
        current_user_id = get_jwt_identity()  # Assuming user ID is stored in the JWT token as a string
        if current_user_id != str(user_id):
            return {'message': 'Unauthorized access'}, 401

        # Query user information
        user = User.query.get(user_id)
        
        if user is None:
            return {'message': 'User not found'}, 404

        # Update user attributes based on request data
        data = request.json  # Assuming JSON data is sent in the request
        if data:
            if 'name' in data:
                user.name = data['name']
            if 'email' in data:
                user.email = data['email']
            if 'image' in data:
                user.image = data['image']
            if 'phone_number' in data:
                if validate_phone_number(data['phone_number']):
                    user.phone_number = data['phone_number']
                else:
                    return {'message': 'Invalid phone number format'}, 400
            if 'profession' in data:
                user.profession = data['profession']
            if 'about' in data:
                user.about = data['about']
        
            # Commit the changes to the database
            db.session.commit()

            # Return a success message
            return {'message': 'User updated successfully'}, 200
        else:
            return {'message': 'No data provided'}, 400


class DeleteUser(Resource):
    @jwt_required()
    def delete(self, user_id):
        current_user_id = get_jwt_identity()
        if current_user_id != str(user_id):
            return {'message': 'Unauthorized access'}, 401

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
api.add_resource(DeleteUser, '/delete_user/<int:user_id>')
api.add_resource(UpdatePassword, '/update_password')
# Resource for creating an event
class EventCreation(Resource):
    @jwt_required()  # Require authentication with JWT
    def post(self):
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()

        if not user:
            return make_response(jsonify({'message': 'User not found'}), 404)

        data = request.get_json()

        # Extracting event details from the request payload
        title = data.get('title')
        description = data.get('description')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        location = data.get('location')
        recurrence = data.get('recurrence')

        # Convert string representations to datetime objects
        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M:%S")

        # Creating a new event
        new_event = Event(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
            recurrence=recurrence,
            created_by=user.id
        )

        # If recurrence is specified, generate and store recurrences in the database
        if recurrence:
            frequency = data.get('frequency')
            interval = data.get('interval')
            byweekday = data.get('byweekday')
            bymonthday = data.get('bymonthday')
            count = data.get('count')

            recurrences = generate_recurrences(
                start_time=start_time,
                recurrence=recurrence,
                frequency=frequency,
                interval=interval,
                byweekday=byweekday,
                bymonthday=bymonthday,
                count=count
            )

            for recurrence_time in recurrences:
                # Ensure end_time is a datetime object for each recurrence event
                recurrence_end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M:%S")

                recurrence_event = Event(
                    title=title,
                    description=description,
                    start_time=datetime.strptime(recurrence_time, "%Y-%m-%dT%H:%M:%S"),
                    end_time=recurrence_end_time,
                    location=location,
                    recurrence=recurrence,
                    created_by=user.id
                )
                db.session.add(recurrence_event)

        # Adding the event to the database session and committing the changes
        db.session.add(new_event)
        db.session.commit()

        return make_response(jsonify({'message': 'Event created successfully'}), 201)

# Adding the EventCreation resource to the API
api.add_resource(EventCreation, '/create_event')

class EventGuests(Resource):
    @jwt_required()  # Require authentication with JWT
    def post(self, event_id):
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()

        if not user:
            return make_response(jsonify({'message': 'User not found'}), 404)

        event = Event.query.filter_by(id=event_id, created_by=user.id).first()

        if not event:
            return make_response(jsonify({'message': 'Event not found or unauthorized'}), 404)

        data = request.get_json()
        guest_email = data.get('guest_email')

        # Check if the guest email corresponds to a valid user
        guest_user = User.query.filter_by(email=guest_email).first()

        if not guest_user:
            return make_response(jsonify({'message': 'Guest not found'}), 404)

        # Check if the guest is already added to the event
        existing_attendee = Attendee.query.filter_by(event_id=event.id, user_id=guest_user.id).first()

        if existing_attendee:
            return make_response(jsonify({'message': 'Guest is already added to the event'}), 400)

        # Add the guest as an attendee to the event
        new_attendee = Attendee(event_id=event.id, user_id=guest_user.id)
        db.session.add(new_attendee)
        db.session.commit()

        return make_response(jsonify({'message': 'Guest added to the event successfully'}), 201)

    @jwt_required()  # Require authentication with JWT
    def get(self, event_id):
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()

        if not user:
            return make_response(jsonify({'message': 'User not found'}), 404)

        event = Event.query.filter_by(id=event_id, created_by=user.id).first()

        if not event:
            return make_response(jsonify({'message': 'Event not found or unauthorized'}), 404)

        # Get all attendees for the event
        attendees = Attendee.query.filter_by(event_id=event.id).all()
        attendee_emails = [User.query.get(attendee.user_id).email for attendee in attendees]

        return make_response(jsonify({'attendees': attendee_emails}), 200)


# Adding the EventCreation and EventGuests resources to the API

api.add_resource(EventGuests, '/event_guests/<int:event_id>')



class EventManagement(Resource):
    @jwt_required()
    def put(self, event_id):
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()

        if not user:
            return make_response(jsonify({'message': 'User not found'}), 404)

        event = Event.query.filter_by(id=event_id, created_by=user.id).first()

        if not event:
            return make_response(jsonify({'message': 'Event not found or unauthorized'}), 404)

        data = request.get_json()

        # Update event details if provided in the request payload
        if 'title' in data:
            event.title = data['title']
        if 'description' in data:
            event.description = data['description']
        if 'start_time' in data:
            event.start_time = datetime.strptime(data['start_time'], "%Y-%m-%dT%H:%M:%S")
        if 'end_time' in data:
            event.end_time = datetime.strptime(data['end_time'], "%Y-%m-%dT%H:%M:%S")


        if 'location' in data:
            event.location = data['location']
        if 'recurrence' in data:
            event.recurrence = data['recurrence']

        db.session.commit()

        return make_response(jsonify({'message': 'Event updated successfully'}), 200)

    @jwt_required()
    def delete(self, event_id):
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()

        if not user:
            return make_response(jsonify({'message': 'User not found'}), 404)

        event = Event.query.filter_by(id=event_id, created_by=user.id).first()

        if not event:
            return make_response(jsonify({'message': 'Event not found or unauthorized'}), 404)

        db.session.delete(event)
        db.session.commit()

        return make_response(jsonify({'message': 'Event deleted successfully'}), 200)


# Adding the EventManagement resource to the API
api.add_resource(EventManagement, '/manage_event/<int:event_id>')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5555)