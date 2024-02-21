from faker import Faker
from random import randint
from datetime import datetime, timedelta
from app import app, db, User, Event, Attendee, CalendarShare

fake = Faker()

def seed_data():
    with app.app_context():
        # Delete all existing records
        db.session.query(User).delete()
        db.session.query(Event).delete()
        db.session.query(Attendee).delete()
        db.session.query(CalendarShare).delete()
        db.session.commit()

        # Create some users
        users = []
        for _ in range(10):
            user = User(
                name=fake.name(),
                email=fake.email(),
                password=fake.password(),
                image=fake.binary(length=1024),
                phone_number=fake.phone_number(),
                profession=fake.job(),
                about=fake.text()
            )
            users.append(user)

        db.session.add_all(users)
        db.session.commit()

        # Create some events
        events = []
        for _ in range(20):
            event = Event(
                title=fake.catch_phrase(),
                description=fake.text(),
                start_time=datetime.now() + timedelta(days=randint(1, 30)),
                end_time=datetime.now() + timedelta(days=randint(31, 60)),
                location=fake.address(),
                created_by=fake.random_element(elements=[user.id for user in users]),
                recurrence=randint(0, 3)
            )
            events.append(event)

        db.session.add_all(events)
        db.session.commit()

        # Create attendees for events
        for event in events:
            num_attendees = randint(1, len(users))
            attendees = fake.random_elements(elements=users, length=num_attendees, unique=True)
            for attendee in attendees:
                db.session.add(Attendee(event_id=event.id, user_id=attendee.id, status=fake.random_element(elements=['confirmed', 'pending', 'declined']), comment=fake.text()))

        db.session.commit()

        # Create calendar shares
        for user in users:
            num_shared_with = randint(1, len(users) - 1)  # Share with at most all other users except self
            shared_with = fake.random_elements(elements=[u for u in users if u != user], length=num_shared_with, unique=True)
            for shared_user in shared_with:
                db.session.add(CalendarShare(calendar_owner_id=user.id, access_granted_to_id=shared_user.id))

        db.session.commit()

        print("Seed data generated successfully!")

if __name__ == "__main__":
    seed_data()