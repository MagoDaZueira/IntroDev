from sqlmodel import Session
from db.models import User, Attempt


def create_new_user(session: Session, username: str, bio: str, password: str):
    new_user = User(
        username=username,
        bio=bio,
        password=password
    )

    session.add(new_user)


def create_attempt(session: Session, attempt: Attempt):
    session.add(attempt)
    return attempt