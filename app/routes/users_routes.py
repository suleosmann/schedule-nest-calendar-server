from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User
from ..validation import is_valid_email, validate_phone_number

from .. import db

users_bp = Blueprint('users', __name__)
api = Api(users_bp)

class UserInfo(Resource):
    # @jwt_required()
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
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return {'message': 'Unauthorized access'}, 401

        user_to_edit = User.query.get_or_404(user_id)

        data = request.json
        if data:
            if 'phone_number' in data:
                # Assuming validate_phone_number is a function you have defined
                if validate_phone_number(data['phone_number']):
                    user_to_edit.phone_number = data['phone_number']
                else:
                    return {'message': 'Invalid phone number format'}, 400

            # Update other fields if they exist in the data
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

            # Commit changes to the database
            db.session.commit()
            return {'message': 'User updated successfully'}, 200
        else:
            return {'message': 'No data provided'}, 400

class DeleteUser(Resource):
    @jwt_required()
    def delete(self, user_id):
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
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
    

class GetAllUsers(Resource):
    @jwt_required()
    def get(self):
        # Query all users
        users = User.query.all()
        
        # Serialize user data including user ID, name, and email
        serialized_users = [{"id": user.id, "name": user.name, "email": user.email} for user in users]
        
        # Check if users are found
        if len(serialized_users) < 1:
            return {'message': 'No users found'}, 404
        
        # Return the serialized users
        return jsonify(serialized_users), 200



# Add resources to the Api
api.add_resource(GetAllUsers, '/get_all_users')
api.add_resource(UserInfo, '/user_info/<int:user_id>')
api.add_resource(EditUser, '/edit_user/<int:user_id>')
api.add_resource(DeleteUser, '/delete_user/<int:user_id>')
