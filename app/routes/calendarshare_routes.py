# app/routes/calendarshare_routes.py

from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import CalendarShare, User, Event,Attendee, db  # Import the CalendarShare model from app.models

calendarshare_bp = Blueprint('calendarshare', __name__)
api = Api(calendarshare_bp)

class CalendarShareResource(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()  # Get the user ID from JWT
        if current_user_id is None:
            return {'message': 'User not authenticated'}, 401
        
        data = request.get_json()
        access_granted_to_id = data.get('user_id')
        
        already_linked = CalendarShare.query.filter_by(
            calendar_owner_id=current_user_id,
            access_granted_to_id=access_granted_to_id
        ).first()

        if already_linked:
            return {'message': 'Users already linked'}, 200

        # Create a new CalendarShare entry
        calendarshare = CalendarShare(
            calendar_owner_id=current_user_id,  # Use the current user's ID as calendar_owner_id
            access_granted_to_id=access_granted_to_id  # Use the user_id from the request as access_granted_to_id
        )

        # Add and commit the new calendar share
        db.session.add(calendarshare)
        db.session.commit()

        return {'message': 'Calendar shared successfully'}, 201

# Adding the CalendarShare resource to the calendarshare API
api.add_resource(CalendarShareResource, '/share_calendar')


from flask_jwt_extended import jwt_required, get_jwt_identity

class CalendarOwnerResource(Resource):
    @jwt_required()
    def get(self):
        access_granted_to_id = get_jwt_identity()  # Get the access_granted_to_id from JWT
        if access_granted_to_id is None:
            return {'message': 'User not authenticated'}, 401
        
        # Query all calendar shares for the given access_granted_to_id
        calendar_shares = CalendarShare.query.filter_by(access_granted_to_id=access_granted_to_id).all()
        if not calendar_shares:
            return {'message': 'Calendar owners not found'}, 404
        
        calendar_owners = []
        for calendar_share in calendar_shares:
            # Query the user table to find the user with the specified calendar_owner_id
            calendar_owner = User.query.get(calendar_share.calendar_owner_id)
            if calendar_owner:
                calendar_owners.append({
                    'user_id': calendar_owner.id,
                    'name': calendar_owner.name
                })
        
        if not calendar_owners:
            return {'message': 'Calendar owners not found'}, 404

        # Return the names and user IDs of all calendar owners associated with the access_granted_to_id
        return calendar_owners, 200

api.add_resource(CalendarOwnerResource, '/get_share_calendar')



class UserCalendarEvents(Resource):
    def get(self, user_id):
        # You may need to import necessary modules and classes
        
        user_created_events = Event.query.filter_by(created_by=user_id).all()
        events_attending = db.session.query(Attendee.event_id).filter_by(user_id=user_id).all()
        event_ids_attending = [event_id[0] for event_id in events_attending]
        user_attending_events = Event.query.filter(Event.id.in_(event_ids_attending)).all()
        all_user_events = user_created_events + user_attending_events
        serialized_events = [event.to_dict() for event in all_user_events]
        
        return serialized_events

api.add_resource(UserCalendarEvents, '/get_shared_calendar/<int:user_id>')


# class CreateShareEvent(Resource):
#     @jwt_required
#     def get(self):
#         current_user = get_jwt_identity()
#         data = request.get_json()
#         access_granted_to_id = data.get('user_id')
        
        
        
