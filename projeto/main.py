from fastapi import FastAPI, HTTPException, Request, Form, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select, delete, SQLModel, create_engine, func
from models import User, Attempt
from pydantic import BaseModel
from typing import Annotated


from utils.verify_attempt import verify_attempt
from utils.password import hash_password, verify_password

arquivo_sqlite = "projeto.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

app = FastAPI()

templates = Jinja2Templates(directory=["templates"])
app.mount("/static", StaticFiles(directory="static"), name="static")


class UserBase(BaseModel):
    username: str
    bio: str
    password: str


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


def get_active_user(session_user: Annotated[str | None, Cookie()] = None):
    if not session_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    with Session(engine) as session:
        user = get_user_by_name(session, session_user)
        return user


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        if request.headers.get("HX-Request"):
            return HTMLResponse(
                status_code=200, 
                headers={"HX-Redirect": "/login"}
            )

        return RedirectResponse(url="/login", status_code=303)

    return HTMLResponse(content=exc.detail, status_code=exc.status_code)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, user: User = Depends(get_active_user)):
    return templates.TemplateResponse(request, "main.html", context={"user": user})


@app.get("/signup", response_class=HTMLResponse)
async def get_signup(request: Request):
    return templates.TemplateResponse(request, "signup.html")


@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.post("/login")
async def post_login(username: str = Form(...), password: str = Form(...)):
    with Session(engine) as session:
        try:
            user = get_user_by_name(session, username)
        except HTTPException:
            return HTMLResponse('<p>User not found</p>')
        if not verify_password(password, user.password):
            return HTMLResponse('<p>Incorrect password</p>')

        response = Response()
        response.headers["HX-Redirect"] = "/"
        response.set_cookie(key="session_user", value=user.username)
        return response


@app.post("/user")
async def create_user(username: str = Form(...), bio: str = Form(""), password: str = Form(...)):
    with Session(engine) as session:
        user_db = session.exec(select(User).where(User.username == username)).first()
        if user_db:
            return HTMLResponse('<p>Username already exists</p>')

        new_user = User(
            username=username,
            bio=bio,
            password=hash_password(password)
        )

        session.add(new_user)
        session.commit()

        response = Response()
        response.headers["HX-Redirect"] = "/login"
        return response


@app.post("/attempt")
async def add_attempt(attempt: Attempt):
    if not verify_attempt(attempt):
        raise HTTPException(status_code=400, detail="Invalid attempt")

    with Session(engine) as session:
        session.add(attempt)
        session.commit()
        session.refresh(attempt)
        return attempt


def get_user_by_name(session: Session, username: str) -> User:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/user/{username}/attempts")
async def get_user_attempts(username: str):
    with Session(engine) as session:
        user = get_user_by_name(session, username)
        return user.attempts


@app.get("/user/{username}/wpm")
async def get_user_wpm(username: str):
    with Session(engine) as session:
        user = get_user_by_name(session, username)
        query = select(func.max(Attempt.wpm)).where(Attempt.user_id == user.id)
        return session.exec(query).first()


@app.get("/user/{username}/playtime")
async def get_total_time(username: str):
    with Session(engine) as session:
        user = get_user_by_name(session, username)

        total = session.exec(
            select(func.sum(Attempt.duration))
            .where(Attempt.user_id == user.id)
        ).first()

        return total or 0


@app.patch("/user/{username}/bio")
async def update_bio(username: str, bio: str):
    with Session(engine) as session:
        user = get_user_by_name(session, username)
        user.bio = bio
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@app.patch("/user/{username}/username")
async def update_username(username: str, new_username: str):
    with Session(engine) as session:
        user = get_user_by_name(session, username)

        user_new_name = session.exec(select(User).where(User.username == new_username)).first()
        if user_new_name:
            raise HTTPException(status_code=400, detail="Username already exists")

        user.username = new_username
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


async def delete_attempts(user_id: int):
    with Session(engine) as session:
        session.exec(delete(Attempt).where(Attempt.user_id == user_id))
        session.commit()

@app.delete("/user/{username}")
async def delete_user(username: str):
    with Session(engine) as session:
        user = get_user_by_name(session, username)
        await delete_attempts(user.id)
        session.exec(delete(User).where(User.username == username))
        session.commit()

    return {"message": "User deleted successfully"}