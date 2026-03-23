from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select, SQLModel, create_engine, func
from models import User, Attempt

from utils.verify_attempt import verify_attempt

arquivo_sqlite = "projeto.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/user")
async def create_user(user: User):
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@app.post("/attempt")
async def add_attempt(attempt: Attempt):
    if not verify_attempt(attempt):
        raise HTTPException(status_code=400, detail="Invalid attempt")

    with Session(engine) as session:
        session.add(attempt)
        session.commit()
        session.refresh(attempt)
        return attempt


@app.get("/user/{user_id}/data")
async def get_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user


@app.get("/user/{user_id}/attempts")
async def get_user_attempts(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.attempts


@app.get("/user/{user_id}/wpm")
async def get_user_wpm(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        query = select(func.max(Attempt.wpm)).where(Attempt.user_id == user_id)
        return session.exec(query).first()