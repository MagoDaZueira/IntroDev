from fastapi import HTTPException
from sqlmodel import Session, select
from models import User


async def update_bio(user: User, bio: str, session: Session):
    user.bio = bio
    session.add(user)


async def update_username(user: User, username: str, session: Session):
    user_new_name = session.exec(select(User).where(User.username == username)).first()
    if user_new_name:
        raise HTTPException(status_code=400, detail="Username already exists")

    user.username = username
    session.add(user)