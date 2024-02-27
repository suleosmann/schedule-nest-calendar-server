from datetime import datetime, timedelta
from dateutil import rrule

def weekday_str_to_int(day_str):
    # Map weekday string to integer
    weekdays_mapping = {'mo': 0, 'tu': 1, 'we': 2, 'th': 3, 'fr': 4, 'sa': 5, 'su': 6}
    return weekdays_mapping.get(day_str.lower(), 0)  # Default to 0 if not found

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

    # Example: handle daily recurrence for 5 occurrences with a default interval of 1
    if recurrence == 'daily':
        recurrence_rule = rrule.rrule(
            rrule.DAILY,
            dtstart=start_datetime,
            count=count,
            interval=interval or 1  # Default to 1 if interval is not provided
        )
        recurrences = [dt.strftime('%Y-%m-%dT%H:%M:%S') for dt in recurrence_rule]

    # Example: handle weekly recurrence for 5 occurrences on specified weekdays
    elif recurrence == 'weekly':
        # Convert weekday strings to integers
        byweekday_int = [weekday_str_to_int(day_str) for day_str in byweekday]
        recurrence_rule = rrule.rrule(
            rrule.WEEKLY,
            byweekday=byweekday_int,
            dtstart=start_datetime,
            count=int(count),
            interval=int(interval)
        )
        recurrences = [dt.strftime('%Y-%m-%dT%H:%M:%S') for dt in recurrence_rule]

    # Example: handle monthly recurrence for 5 occurrences on specified month days
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
