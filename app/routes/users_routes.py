from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token, verify_jwt_in_request
from ..models import User, Attendee, Event
from ..validation import is_valid_email, validate_phone_number
from functools import wraps
from .. import db

users_bp = Blueprint('users', __name__)
api = Api(users_bp)

def jwt_or_refresh_token_required(fn):
    """
    Custom decorator to accept either JWT access token or refresh token.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # Try to verify JWT token in request headers
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except:
            try:
                # Try to get JWT identity
                get_jwt_identity()
                return fn(*args, **kwargs)
            except:
                return {'message': 'Missing or invalid token'}, 401
    return wrapper

class UserInfo(Resource):
    @jwt_or_refresh_token_required
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return {'message': 'User not found'}, 404

        serialized_user = user.to_dict()
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
    def patch(self):
        current_user_id = get_jwt_identity()
        user_to_edit = User.query.get_or_404(current_user_id)
        data = request.json

        if not data:
            return {'message': 'No data provided'}, 400

        if 'phone_number' in data and validate_phone_number(data['phone_number']):
            user_to_edit.phone_number = data['phone_number']
        if 'name' in data:
            user_to_edit.name = data['name']
        if 'email' in data:
            user_to_edit.email = data['email']
        if 'image' in data:
            user_to_edit.image = data['image']
        if 'profession' in data:
            user_to_edit.profession = data['profession']
        if 'about' in data:
            user_to_edit.about = data['about']

        db.session.commit()
        return {'message': 'User updated successfully'}, 200 if data else 400

class DeleteUser(Resource):
    @jwt_required()
    def delete(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if user is None:
            return {'message': 'User not found'}, 404
        
        db.session.delete(user)
        db.session.commit()
        
        return {'message': 'User deleted successfully'}, 200


class GetAllUsers(Resource):
    def get(self):
        users = User.query.all()
        serialized_users = []
        for user in users:
            serialized_user = {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
            serialized_users.append(serialized_user)
        
        if len(serialized_users) < 1:
            return {'message': 'No users found'}, 404
        
        return serialized_users, 200

class UserCalendarEvents(Resource):  
    @jwt_required()
    def get(self):      
        current_user_id = get_jwt_identity()
        
        user_created_events = Event.query.filter_by(created_by=current_user_id).all()
        events_attending = db.session.query(Attendee.event_id).filter_by(user_id=current_user_id).all()
        event_ids_attending = [event_id[0] for event_id in events_attending]
        user_attending_events = Event.query.filter(Event.id.in_(event_ids_attending)).all()
        all_user_events = user_created_events + user_attending_events
        serialized_events = [event.to_dict() for event in all_user_events]
        
        return serialized_events


    
    


# Add resources to the Api
api.add_resource(GetAllUsers, '/get_all_users')
api.add_resource(UserInfo, '/user_info')
api.add_resource(EditUser, '/edit_user')
api.add_resource(DeleteUser, '/delete_user')
api.add_resource(UserCalendarEvents, '/calendar-events')

