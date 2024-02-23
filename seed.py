from faker import Faker
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Event
import random

fake = Faker()

# Function to create fake users
def create_users(num_users):
    users = []
    for i in range(1, num_users + 1):
        user = User(
            name=fake.name(),
            email=fake.email(),
            password=f"Pass#word{i}"  # Use provided password with incremented number
        )
        users.append(user)
    db.session.add_all(users)
    db.session.commit()
    return users

# Function to create fake events
def create_events(users, num_events_per_user):
    events = []
    for user in users:
        for _ in range(num_events_per_user):
            title = fake.sentence(nb_words=3, variable_nb_words=True, ext_word_list=None)
            description = fake.paragraph(nb_sentences=3, variable_nb_sentences=True, ext_word_list=None)
            start_time = fake.date_time_between(start_date="-1y", end_date="+1y", tzinfo=None)
            end_time = start_time + timedelta(hours=random.randint(1, 5))
            location = fake.address()
            recurrence = random.choice([None, 'daily', 'weekly', 'monthly', 'yearly'])

            event = Event(
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
                location=location,
                recurrence=recurrence,
                created_by=user.id
            )
            events.append(event)

    db.session.add_all(events)
    db.session.commit()
    return events

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        num_users = 5
        num_events_per_user = 3

        # Create users
        users = create_users(num_users)

        # Create events
        create_events(users, num_events_per_user)

        print("Database seeded successfully!")
