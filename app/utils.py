# app/utils.py

from .models import CalendarShare, db
from datetime import datetime


def delete_expired_entries():
    try:
        # Query and delete expired entries
        expired_entries = CalendarShare.query.filter(CalendarShare.expiration_time < datetime.utcnow()).all()
        for entry in expired_entries:
            db.session.delete(entry)
        db.session.commit()
        print("Expired entries deleted successfully")
    except Exception as e:
        print(f"Error deleting expired entries: {str(e)}")