from typing import List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    bio: str
    password: str

    attempts: List["Attempt"] = Relationship(back_populates="user")


class Attempt(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    wpm: float
    accuracy: float
    date: datetime = Field(default_factory=datetime.now)
    duration: int
    user_id: int = Field(foreign_key="user.id")

    user: "User" = Relationship(back_populates="attempts")