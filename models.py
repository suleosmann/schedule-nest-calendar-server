from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    # Serializing the User model with the Profile model
    serialize_rules = ('-profiles.user',)

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    email = db.Column(db.String(100), unique = True, nullable = False)
    password = db.Column(db.String)

class Profile(db.Model, SerializerMixin):
    __tablename__ = 'profiles'

    # Serialization rules with the Users model
    serialize_rules = ('-user.profiles',)

    id = db.Column(db.Integer, primary_key = True)
    image = db.Column(db.LargeBinary) 
    phone_number = db. Column(db.String(20))
    profession = db.Column(db.String(100))
    about = db.Column(db.Text)  

class Event(db.Model, SerializerMixin):
    __tablename__ = 'events'

    # Serialization rules with the attendees table
    serialize_rules = ('-attendees.event',)
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Corrected foreign key constraint
    recurrence = db.Column(db.Integer, default=0)
    user = db.relationship('User', backref='events')


class Attendee(db.Model, SerializerMixin):
    __tablename__ = 'attendees'

    # Serialization rules with the events table
    serialize_rules = ('event.attendees',) 

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)  # Reference to the event
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Reference to the user who is attending the event
    status = db.Column(db.String(50))  # Example: status of the attendee, e.g., 'confirmed', 'pending', etc.
    comment = db.Column(db.String(255))  # Example: a comment from the attendee regarding the event

    # Define relationships with Events and User Models
    event = db.relationship('Event', backref='attendees')
    user = db.relationship('User', backref='attendees')   
    

class CalendarShare(db.Model, SerializerMixin):
    __tablename__ = 'calendarshares'

    id = db.Column(db.Integer, primary_key=True) 
    calendar_owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    access_granted_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Define relationships with the User model
    calendar_owner = db.relationship('User', foreign_keys=[calendar_owner_id], backref='calendar_owner_shares')
    access_granted_to = db.relationship('User', foreign_keys=[access_granted_to_id], backref='access_granted_to_shares')



