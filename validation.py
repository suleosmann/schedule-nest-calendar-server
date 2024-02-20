import re
import email_validator

def is_valid_email(email):
    # Check if email is empty
    if not email:
        return False
    
    # Use regular expression to validate email format
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return False
    
    # Use email-validator package to perform additional validation
    try:
        email_validator.validate_email(email)
        return True
    except email_validator.EmailNotValidError:
        return False
