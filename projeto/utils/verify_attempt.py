import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.models import Attempt

def verify_attempt(attempt: Attempt):
    if attempt.wpm > 350:
        return False
    if attempt.accuracy < 0 or attempt.accuracy > 350:
        return False
    return True