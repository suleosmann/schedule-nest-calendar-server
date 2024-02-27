from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Event, Attendee, db

attendees_bp = Blueprint('attendees', __name__)
api = Api(attendees_bp)

class EventGuests(Resource):
    @jwt_required()  # Require authentication with JWT
    def post(self, event_id):
        current_user_id = get_jwt_identity()
        event = Event.query.filter_by(id=event_id, created_by=current_user_id).first()

        if not event:
            return make_response(jsonify({'message': 'Event not found or unauthorized'}), 404)

        data = request.get_json()
        guest_id = data.get('guest_id')

        if not isinstance(guest_id, list):
            return make_response(jsonify({'message': 'Invalid input format. Expected list of guest emails.'}), 400)

        for guest_id in guest_id:
            # Check if the guest email corresponds to a valid user
            guest_user = User.query.filter_by(id=guest_id).first()

            if not guest_user:
                return make_response(jsonify({'message': f'User with id {guest_id} not found'}), 404)

            # Check if the guest is already added to the event
            existing_attendee = Attendee.query.filter_by(event_id=event.id, user_id=guest_user.id).first()

            if existing_attendee:
                # If the guest is already added to the event, continue to the next email
                continue

            # Add the guest as an attendee to the event
            new_attendee = Attendee(event_id=event.id, user_id=guest_user.id)
            db.session.add(new_attendee)

        # Commit all changes to the database
        db.session.commit()

        if len(guest_id) == 1 and existing_attendee:
            return make_response(jsonify({'message': 'Guest is already added to the event'}), 400)
        else:
            return make_response(jsonify({'message': 'Guests added to the event successfully'}), 201)
        
    @jwt_required()  # Require authentication with JWT
    def get(self, event_id):
        current_user_id = get_jwt_identity()
        event = Event.query.filter_by(id=event_id).first()

        if not event:
            return make_response(jsonify({'message': 'Event not found'}), 404)

        if event.created_by != current_user_id:
            return make_response(jsonify({'message': 'No authorization to access this event'}), 403)

        # Get all attendees for the event
        attendees = Attendee.query.filter_by(event_id=event.id).all()
        attendee_emails = [User.query.get(attendee.user_id).email for attendee in attendees]

        return make_response(jsonify({'attendees': attendee_emails}), 200)


# Adding the EventGuests resource to the API
api.add_resource(EventGuests, '/event_guests/<int:event_id>')
