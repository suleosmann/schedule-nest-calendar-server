from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Event
from datetime import datetime
from ..recurrence_helper import generate_recurrences
from .. import db
from dateutil.rrule import rrule, rruleset, MO, TU, WE, TH, FR, SA, SU


# Utility function to convert weekday string to integer
def convert_to_weekday_integer(day_str):
    # Map weekday string to integer
    weekdays_mapping = {'mo': 0, 'tu': 1, 'we': 2, 'th': 3, 'fr': 4, 'sa': 5, 'su': 6}
    return weekdays_mapping.get(day_str.lower(), 0)  # Default to 0 if not found

# Utility function for formatting datetime objects
def format_datetime(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")

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

        # Example conversion from string to integer for byweekday values
        byweekday = [convert_to_weekday_integer(day_str) for day_str in data.get('byweekday', [])]
        import pdb; pdb.set_trace()

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

            for recurrence_time, recurrence_end_time in recurrences:
                recurrence_event = Event(
                    title=title,
                    description=description,
                    start_time=datetime.strptime(recurrence_time, "%Y-%m-%dT%H:%M:%S"),
                    end_time=datetime.strptime(recurrence_end_time, "%Y-%m-%dT%H:%M:%S"),
                    location=location,
                    recurrence=recurrence,
                    created_by=user.id
                )
                db.session.add(recurrence_event)

        # Adding the event to the database session and committing the changes
        db.session.add(new_event)
        db.session.commit()

        # Include event details in the response
        response_data = {
            'message': 'Event created successfully',
            'event': {
                'id': new_event.id,
                'title': new_event.title,
                'description': new_event.description,
                'start_time': format_datetime(new_event.start_time),
                'end_time': format_datetime(new_event.end_time),
                'location': new_event.location,
                'recurrence': new_event.recurrence,
                'created_by': new_event.created_by
            }
        }

        return make_response(jsonify(response_data), 201)


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

# Endpoint to fetch all calendar events
class Events(Resource):
    @jwt_required()
    def get(self):
        events = []
        for event in Event.query.all():
            event_dict = event.to_dict()
            events.append(event_dict)

        response = make_response(
            jsonify(events),
            200
        )

        return response

# Adding Event Fetching Resource to the API
api.add_resource(Events, '/get_events')
