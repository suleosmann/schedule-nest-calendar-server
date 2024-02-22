# recurrence_helper.py

from datetime import datetime, timedelta
from dateutil import rrule

def generate_recurrences(start_time, recurrence, frequency, interval, byweekday, bymonthday, count):
    """
    Generate recurring events based on the start_time and recurrence pattern.
    """
    recurrences = []

    # Parse start_time to datetime object if it's not already a string
    if isinstance(start_time, datetime):
        start_datetime = start_time
    else:
        start_datetime = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')

    # Example: handle daily recurrence for 5 occurrences
    if recurrence == 'daily':
        recurrence_rule = rrule.rrule(
            rrule.DAILY,
            dtstart=start_datetime,
            count=5  # Adjust the number of recurrences as needed
        )
        recurrences = [dt.strftime('%Y-%m-%dT%H:%M:%S') for dt in recurrence_rule]

    # Example: handle weekly recurrence for 5 occurrences on Mondays and Wednesdays
    elif recurrence == 'weekly':
        recurrence_rule = rrule.rrule(
            rrule.WEEKLY,
            byweekday=[rrule.MO, rrule.WE],
            dtstart=start_datetime,
            count=5
        )
        recurrences = [dt.strftime('%Y-%m-%dT%H:%M:%S') for dt in recurrence_rule]

    # Example: handle monthly recurrence for 5 occurrences on the 15th of each month
    elif recurrence == 'monthly':
        recurrence_rule = rrule.rrule(
            rrule.MONTHLY,
            bymonthday=[15],
            dtstart=start_datetime,
            count=5
        )
        recurrences = [dt.strftime('%Y-%m-%dT%H:%M:%S') for dt in recurrence_rule]

    # Add more recurrence patterns as needed

    return recurrences
