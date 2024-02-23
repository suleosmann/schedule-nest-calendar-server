import re
import email_validator

def is_valid_email(email):
    # Check if email is empty
    if not email:
        return False
    
    # Use email-validator package to perform additional validation
    try:
        email_validator.validate_email(email, check_deliverability=False)
        return True
    except email_validator.EmailNotValidError:
        return False

def is_valid_password(password, email):
    # Check if password is empty
    if not password:
        return False
    
    # Check if password meets minimum length requirement (e.g., 8 characters)
    if len(password) < 8:
        return False
    
    # Check if password contains at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False
    
    # Check if password contains at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False
    
    # Check if password contains at least one digit
    if not re.search(r'[0-9]', password):
        return False
    
    # Check if password contains at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    # Check if the password is the same as the email
    if password == email:
        return False
    
    return True


def validate_phone_number(phone_number):
    # Ensure phone_number is a string
    phone_number = str(phone_number)

    # Check if phone number starts with the correct prefixes and has the correct length
    if phone_number.startswith(('+2541', '+2547')) and len(phone_number) == 12:
        # Remove the "+" sign and spaces
        phone_number = phone_number.replace('+', '').replace(' ', '')
        # Check if the remaining characters are digits
        if phone_number.isdigit():
            return True
    return False

