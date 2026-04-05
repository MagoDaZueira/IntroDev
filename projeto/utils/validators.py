import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re
from db.models import Attempt
from utils.constants import MAX_USERNAME_LENGTH, MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH, MAX_BIO_LENGTH

def verify_attempt(attempt: Attempt):
    if attempt.wpm > 350:
        return False
    if attempt.accuracy < 0 or attempt.accuracy > 100:
        return False
    return True

def valid_username(username: str):
    if not username:
        return "Username is required"
    if len(username) > MAX_USERNAME_LENGTH:
        return f"Username must be at most {MAX_USERNAME_LENGTH} characters long"
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return "Usernames can only contain letters, numbers, hyphens, and underscores"
    return ""

def valid_password(password: str):
    if not password:
        return "Password is required"
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
    if len(password) > MAX_PASSWORD_LENGTH:
        return f"Password must be at most {MAX_PASSWORD_LENGTH} characters long"
    return ""

def valid_bio(bio: str):
    if len(bio) > MAX_BIO_LENGTH:
        return f"Bio must be at most {MAX_BIO_LENGTH} characters long"
    return ""