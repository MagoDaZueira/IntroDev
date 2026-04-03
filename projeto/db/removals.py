from sqlmodel import Session, delete
from db.models import User, Attempt
from db.queries import get_user_by_name


def delete_attempts(session: Session, user_id: int):
    session.exec(delete(Attempt).where(Attempt.user_id == user_id))


def delete_user_by_name(session: Session, username: str):
    user = get_user_by_name(session, username)
    delete_attempts(session, user.id)
    session.exec(delete(User).where(User.username == username))

    return {"message": "User deleted successfully"}