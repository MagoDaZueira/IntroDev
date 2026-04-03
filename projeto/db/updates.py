from fastapi import HTTPException
from sqlmodel import Session, select
from db.models import User


def update_bio(session: Session, user: User, bio: str):
    user.bio = bio
    session.add(user)


def update_username(session: Session, user: User, username: str):
    if username != user.username:
        user_new_name = session.exec(select(User).where(User.username == username)).first()
        if user_new_name:
            raise HTTPException(status_code=400, detail="Username already exists")

    user.username = username
    session.add(user)