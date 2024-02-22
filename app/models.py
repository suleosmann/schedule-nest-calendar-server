from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    image = db.Column(db.LargeBinary) 
    phone_number = db.Column(db.String(20))
    profession = db.Column(db.String(100))
    about = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'image': self.image,
            'phone_number': self.phone_number,
            'profession': self.profession,
            'about': self.about
        }

class Event(db.Model, SerializerMixin):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recurrence = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat(),  # Convert datetime to ISO format string
            'end_time': self.end_time.isoformat(),      # Convert datetime to ISO format string
            'location': self.location,
            'created_by': self.created_by,
            'recurrence': self.recurrence
        }

class Attendee(db.Model, SerializerMixin):
    __tablename__ = 'attendees'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50))
    comment = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'user_id': self.user_id,
            'status': self.status,
            'comment': self.comment
        }

class CalendarShare(db.Model, SerializerMixin):
    __tablename__ = 'calendarshares'

    id = db.Column(db.Integer, primary_key=True) 
    calendar_owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    access_granted_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'calendar_owner_id': self.calendar_owner_id,
            'access_granted_to_id': self.access_granted_to_id
        }
