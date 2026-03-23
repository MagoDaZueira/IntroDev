from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select, SQLModel, create_engine
from models import User, Attempt

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
    with Session(engine) as session:
        session.add(attempt)
        session.commit()
        session.refresh(attempt)
        return attempt