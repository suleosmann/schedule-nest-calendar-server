from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Event
from datetime import datetime
from ..recurrence_helper import generate_recurrences
from .. import db


events_bp = Blueprint('events', __name__)
api = Api(events_bp)

class EventCreation(Resource):
    @jwt_required()  # Require authentication with JWT
    def post(self):
        current_user_id = get_jwt_identity()  # Get the user ID from JWT
        if isinstance(current_user_id, int):
            # Handle the case where the identity is an integer
            current_user_id = {'sub': current_user_id}

        user_id = current_user_id.get('sub')
        user = User.query.get(user_id)  # Query the user by ID

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


class EventManagement(Resource):
    @jwt_required()
    def put(self, event_id):
        current_user_id = get_jwt_identity()
        if isinstance(current_user_id, int):
            current_user_id = {'sub': current_user_id}

        user_id = current_user_id.get('sub')
        if not user_id:
            return make_response(jsonify({'message': 'User ID not found in JWT token'}), 400)

        user = User.query.get(user_id)
        if not user:
            return make_response(jsonify({'message': 'User not found'}), 404)

        event = Event.query.filter_by(id=event_id).first()
        if not event:
            return make_response(jsonify({'message': 'Event not found'}), 404)
        elif event.created_by != user.id:
            return make_response(jsonify({'message': 'Unauthorized to edit or delete event'}), 403)

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
        current_user_id = get_jwt_identity()
        if isinstance(current_user_id, int):
            current_user_id = {'sub': current_user_id}

        user_id = current_user_id.get('sub')
        if not user_id:
            return make_response(jsonify({'message': 'User ID not found in JWT token'}), 400)

        user = User.query.get(user_id)
        if not user:
            return make_response(jsonify({'message': 'User not found'}), 404)

        event = Event.query.filter_by(id=event_id).first()
        if not event:
            return make_response(jsonify({'message': 'Event not found'}), 404)
        elif event.created_by != user.id:
            return make_response(jsonify({'message': 'Unauthorized to edit or delete event'}), 403)

        db.session.delete(event)
        db.session.commit()

        return make_response(jsonify({'message': 'Event deleted successfully'}), 200)

# Adding the EventManagement resource to the API
api.add_resource(EventManagement, '/manage_event/<int:event_id>')
