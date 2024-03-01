from datetime import datetime, timedelta
from dateutil import rrule

def weekday_str_to_int(day_str):
    # Map full weekday names to integer
    weekdays_mapping = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}
    return weekdays_mapping.get(day_str, 0)  # Default to 0 if not found

def generate_recurrences(start_time, recurrence, interval=None, byweekday=None, bymonthday=None, count=None):
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

    # Set default values
    interval = int(interval) if interval else 1
    byweekday_int = [weekday_str_to_int(day_str) for day_str in byweekday] if byweekday else None
    bymonthday = int(bymonthday) if bymonthday else None

    # Calculate the end date based on the count parameter
    if count:
        if recurrence == 'weekly':
            end_datetime = start_datetime + timedelta(weeks=int(count))
        elif recurrence == 'monthly':
            end_datetime = start_datetime + timedelta(days=30 * int(count))  # Assuming a month is 30 days
        else:
            end_datetime = start_datetime + timedelta(days=int(count))

    # Example: handle daily recurrence for specified duration with a default interval of 1
    if recurrence == 'daily':
        recurrence_rule = rrule.rrule(
            rrule.DAILY,
            dtstart=start_datetime,
            until=end_datetime,
            interval=interval
        )
        recurrences = [dt.strftime('%Y-%m-%dT%H:%M:%S') for dt in recurrence_rule]

    # Example: handle weekly recurrence for specified duration on specified weekdays
    elif recurrence == 'weekly':
        recurrence_rule = rrule.rrule(
            rrule.WEEKLY,
            byweekday=byweekday_int,
            dtstart=start_datetime,
            until=end_datetime,
            interval=interval
        )
        recurrences = [dt.strftime('%Y-%m-%dT%H:%M:%S') for dt in recurrence_rule]

    # Example: handle monthly recurrence for specified duration on specified month days
    elif recurrence == 'monthly':
        recurrence_rule = rrule.rrule(
            rrule.MONTHLY,
            bymonthday=bymonthday,
            dtstart=start_datetime,
            until=end_datetime,
            interval=interval
        )
        recurrences = [dt.strftime('%Y-%m-%dT%H:%M:%S') for dt in recurrence_rule]

    # Adjust the end time for each recurrence
    recurrences_with_end_time = [(recurrence_time, (datetime.strptime(recurrence_time, "%Y-%m-%dT%H:%M:%S") + (end_time - start_datetime)).strftime('%Y-%m-%dT%H:%M:%S')) for recurrence_time in recurrences]

    return recurrences_with_end_time
