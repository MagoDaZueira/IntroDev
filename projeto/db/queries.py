from fastapi import HTTPException
from sqlmodel import Session, func, select
from models import User, Attempt


def get_user_by_name(session: Session, username: str) -> User:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_attempt_count(session: Session, user_id: int):
    statement = select(func.count()).where(Attempt.user_id == user_id)
    return session.exec(statement).one()


def get_user_attempts(session: Session, username: str):
    user = get_user_by_name(session, username)
    return user.attempts


def get_user_avg_wpm(session: Session, username: str):
    user = get_user_by_name(session, username)
    query = select(func.round(func.avg(Attempt.wpm), 2)).where(Attempt.user_id == user.id)
    return session.exec(query).first() or 0


def get_user_max_wpm(session: Session, username: str):
    user = get_user_by_name(session, username)
    query = select(func.max(Attempt.wpm)).where(Attempt.user_id == user.id)
    return session.exec(query).first() or 0


def get_user_avg_accuracy(session: Session, username: str):
    user = get_user_by_name(session, username)
    query = select(func.round(func.avg(Attempt.accuracy), 2)).where(Attempt.user_id == user.id)
    return session.exec(query).first() or 0


def get_user_max_accuracy(session: Session, username: str):
    user = get_user_by_name(session, username)
    query = select(func.max(Attempt.accuracy)).where(Attempt.user_id == user.id)
    return session.exec(query).first() or 0


def get_total_time(session: Session, username: str):
    user = get_user_by_name(session, username)

    total = session.exec(
        select(func.sum(Attempt.duration))
        .where(Attempt.user_id == user.id)
    ).first()

    return total or 0


def user_dict(username: str, session: Session):
    user = get_user_by_name(session, username)
    avg_wpm = get_user_avg_wpm(session, user.username)
    max_wpm = get_user_avg_wpm(session, user.username)
    avg_accuracy = get_user_avg_accuracy(session, user.username)
    max_accuracy = get_user_avg_accuracy(session, user.username)
    playtime = get_total_time(session, user.username)
    attempts = get_user_attempts(session, user.username)
    attempt_count = get_attempt_count(session, user.id)

    user_info = {
        "username": user.username,
        "bio": user.bio,
        "avg_wpm": avg_wpm,
        "max_wpm": max_wpm,
        "avg_accuracy": avg_accuracy,
        "max_accuracy": max_accuracy,
        "playtime": playtime,
        "attempts": attempts,
        "attempt_count": attempt_count
    }

    return user_info