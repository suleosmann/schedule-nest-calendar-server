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

    # Adjust the end time based on the start time
    end_time = start_datetime + timedelta(hours=1)  # Adjust this as needed

    # Example: handle daily recurrence for 5 occurrences
    if recurrence == 'daily':
        recurrence_rule = rrule.rrule(
            rrule.DAILY,
            dtstart=start_datetime,
            count=count,
            interval=interval
        )
        recurrences = [dt.strftime('%Y-%m-%dT%H:%M:%S') for dt in recurrence_rule]

    # Example: handle weekly recurrence for 5 occurrences on Mondays and Wednesdays
    elif recurrence == 'weekly':
        recurrence_rule = rrule.rrule(
            rrule.WEEKLY,
            byweekday=byweekday,
            dtstart=start_datetime,
            count=count,
            interval=interval
        )
        recurrences = [dt.strftime('%Y-%m-%dT%H:%M:%S') for dt in recurrence_rule]

    # Example: handle monthly recurrence for 5 occurrences on the 15th of each month
    elif recurrence == 'monthly':
        recurrence_rule = rrule.rrule(
            rrule.MONTHLY,
            bymonthday=bymonthday,
            dtstart=start_datetime,
            count=count,
            interval=interval
        )
        recurrences = [dt.strftime('%Y-%m-%dT%H:%M:%S') for dt in recurrence_rule]

    # Adjust the end time for each recurrence
    recurrences_with_end_time = []
    for recurrence_time in recurrences:
        recurrence_end_time = datetime.strptime(recurrence_time, "%Y-%m-%dT%H:%M:%S") + (end_time - start_datetime)
        recurrences_with_end_time.append((recurrence_time, recurrence_end_time.strftime('%Y-%m-%dT%H:%M:%S')))

    return recurrences_with_end_time

