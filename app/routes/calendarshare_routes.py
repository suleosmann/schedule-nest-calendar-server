# app/routes/calendarshare_routes.py

from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import CalendarShare, User, db  # Import the CalendarShare model from app.models

calendarshare_bp = Blueprint('calendarshare', __name__)
api = Api(calendarshare_bp)

class CalendarShareResource(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()  # Get the user ID from JWT
        if current_user_id is None:
            return {'message': 'User not authenticated'}, 401
        
        if isinstance(current_user_id, int):
            # Handle the case where the identity is an integer
            calendar_owner_id = current_user_id
        elif isinstance(current_user_id, dict):
            # Extract user ID from dictionary
            calendar_owner_id = current_user_id.get('sub')
        else:
            return {'message': 'Invalid user identity format'}, 401

        data = request.get_json()
        access_granted_to_email = data.get('access_granted_to_email')

        # Query the user by email to get the user_id of the person receiving the share
        access_granted_to_user = User.query.filter_by(email=access_granted_to_email).first()
        if not access_granted_to_user:
            return {'message': 'User with email {} not found'.format(access_granted_to_email)}, 404

        access_granted_to_id = access_granted_to_user.id

        # Create a new CalendarShare entry
        calendarshare = CalendarShare()
        calendarshare.calendar_owner_id = calendar_owner_id
        calendarshare.access_granted_to_id = access_granted_to_id

        # Add and commit the new calendar share
        db.session.add(calendarshare)
        db.session.commit()

        return {'message': 'Calendar shared successfully'}, 201


# Adding the CalendarShare resource to the calendarshare API
api.add_resource(CalendarShareResource, '/share_calendar')
