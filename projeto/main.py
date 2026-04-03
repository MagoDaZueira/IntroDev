from fastapi import FastAPI, HTTPException, Request, Form, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, SQLModel, create_engine
from pydantic import BaseModel
from typing import Annotated

from db.models import User, Attempt
from db.insertions import *
from db.queries import *
from db.updates import *
from db.removals import *

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


def get_session():
    with Session(engine) as session:
        yield session


def get_optional_user(session_user: Annotated[str | None, Cookie()] = None, session: Session = Depends(get_session)):
    if not session_user:
        return None
    try:
        user = get_user_by_name(session, session_user)
    except HTTPException:
        user = None
    return user


def get_active_user(session_user: Annotated[str | None, Cookie()] = None, session: Session = Depends(get_session)):
    if not session_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

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
    return templates.TemplateResponse(request, "/layouts/main.html", context={"user": user})


@app.get("/signup", response_class=HTMLResponse)
async def get_signup(request: Request):
    return templates.TemplateResponse(request, "/layouts/signup.html")


@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse(request, "/layouts/login.html")


@app.post("/login")
async def post_login(username: str = Form(...), password: str = Form(...), session: Session = Depends(get_session)):
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
async def create_user(username: str = Form(...), bio: str = Form(""), password: str = Form(...), session: Session = Depends(get_session)):
    try:
        get_user_by_name(session, username)
        return HTMLResponse('<p>Username already exists</p>')
    except HTTPException:
        pass

    create_new_user(session, username, bio, hash_password(password))
    session.commit()

    response = Response()
    response.headers["HX-Redirect"] = "/login"
    return response


@app.post("/attempt")
async def add_attempt(attempt: Attempt, session: Session = Depends(get_session)):
    if not verify_attempt(attempt):
        raise HTTPException(status_code=400, detail="Invalid attempt")

    create_attempt(session, attempt)
    session.commit()
    session.refresh(attempt)
    return attempt


@app.get("/user/{username}")
async def public_user_page(request: Request, username: str, session: Session = Depends(get_session), active_user = Depends(get_optional_user)):
    user_info = user_dict(username, session)
    active_username = active_user.username if active_user else None
    return templates.TemplateResponse(request, "/layouts/profile.html", context={"user": user_info, "active_username": active_username})


@app.get("/user/{username}/edit")
def edit_profile_page(request: Request, username: str, session: Session = Depends(get_session)):
    if not request.headers.get("HX-Request"):
        return RedirectResponse(url="/profile")
    user = get_user_by_name(session, username)
    user_info = {
        "username": user.username,
        "bio": user.bio
    }
    return templates.TemplateResponse(request, "/partials/edit_profile.html", context={"user": user_info})


@app.patch("/user/{username}/edit")
def edit_profile(request: Request, username: str, new_username: str = Form(...), new_bio: str = Form(...), session: Session = Depends(get_session)):
    user = get_user_by_name(session, username)
    update_username(session, user, new_username)
    update_bio(session, user, new_bio)
    session.commit()
    user_info = user_dict(new_username, session)
    response = templates.TemplateResponse(
        request,
        "/partials/default_user_info.html",
        context={"user": user_info, "active_username": new_username}
    )
    response.set_cookie(key="session_user", value=new_username)
    response.headers["HX-Push-Url"] = f'/user/{new_username}'
    return response


@app.delete("/user/{username}")
async def delete_user(username: str, session: Session = Depends(get_session)):
    delete_user_by_name(session, username)
    session.commit()

    return {"message": "User deleted successfully"}