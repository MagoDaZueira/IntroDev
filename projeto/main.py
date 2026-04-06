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

from utils.validators import verify_attempt, valid_username, valid_bio, valid_password
from utils.password import hash_password, verify_password
from utils.words_generation import generate_words

from utils.constants import ATTEMPT_PAGINATION_STEP, DEFAULT_TEST_LENGTH, MIN_TEST_LENGTH, MAX_TEST_LENGTH

from datetime import datetime

arquivo_sqlite = "projeto.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

app = FastAPI()

templates = Jinja2Templates(directory=["templates"])
app.mount("/static", StaticFiles(directory="static"), name="static")

WORDS = []


@app.on_event("startup")
def on_startup():
    with open("static/wordlists/english1k.txt") as f:
        global WORDS
        WORDS = [w.strip() for w in f if w.strip()]
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


def render(request: Request, template: str, context: dict):
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(request, template, context)

    return templates.TemplateResponse(
        request,
        "layouts/main.html",
        {**context, "chosen_template": template}
    )


@app.get("/clear")
async def clear_page(request: Request):
    if not request.headers.get("HX-Request"):
        return RedirectResponse(url="/")
    return HTMLResponse("")


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
async def root(request: Request, length: int = DEFAULT_TEST_LENGTH, session: Session = Depends(get_session), active_user: User = Depends(get_optional_user)):
    if not active_user:
        return render(request, "/layouts/typing.html", context={"active_username": None})
    user_info = user_dict(active_user.username, session)
    length = max(MIN_TEST_LENGTH, min(MAX_TEST_LENGTH, length))
    words = generate_words(WORDS, length)
    return render(
        request, "/layouts/typing.html",
        context={"active_username": active_user.username, "user": user_info, "text": words, "length": length}
    )


@app.get("/signup", response_class=HTMLResponse)
async def get_signup(request: Request, active_user: User = Depends(get_optional_user)):
    return render(
        request,
        "/layouts/signup.html",
        context={"active_username": active_user.username if active_user else None}
    )


@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request, active_user: User = Depends(get_optional_user)):
    return render(
        request,
        "/layouts/login.html",
        context={"active_username": active_user.username if active_user else None}
    )


@app.get("/settings", response_class=HTMLResponse)
async def get_settings(request: Request, active_user: User = Depends(get_optional_user)):
    return render(
        request,
        "/layouts/settings.html",
        context={"active_username": active_user.username if active_user else None}
    )


@app.post("/logout")
async def post_logout():
    response = Response()
    response.headers["HX-Redirect"] = "/login"
    response.delete_cookie(key="session_user")
    return response


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

    username_error = valid_username(username)
    bio_error = valid_bio(bio)
    password_error = valid_password(password)

    if username_error or bio_error or password_error:
        error_msg = username_error or bio_error or password_error
        return HTMLResponse(f'<p>{error_msg}</p>')

    create_new_user(session, username, bio, hash_password(password))
    session.commit()

    response = Response()
    response.headers["HX-Redirect"] = "/login"
    return response


@app.post("/attempt")
async def add_attempt(
    request: Request, 
    wpm: float = Form(...), 
    accuracy: float = Form(...), 
    duration: float = Form(...), 
    session: Session = Depends(get_session),
    active_user: User = Depends(get_optional_user)
):

    new_attempt = Attempt(
        wpm=wpm,
        accuracy=accuracy,
        duration=duration,
        date=datetime.now(),
        user_id=active_user.id if active_user else None
    )

    if not verify_attempt(new_attempt):
        return HTMLResponse('<p>Invalid attempt</p>')

    create_attempt(session, new_attempt)
    session.commit()
    session.refresh(new_attempt)

    return render(
        request, 
        "layouts/result.html", 
        context={"attempt": new_attempt, "user": active_user}
    )


@app.get("/user/{username}")
async def user_page(request: Request, username: str, session: Session = Depends(get_session), active_user: User = Depends(get_optional_user)):
    user_info = user_dict(username, session)
    active_username = active_user.username if active_user else None
    return render(request, "/layouts/profile.html", context={"user": user_info, "active_username": active_username})


@app.get("/user/{username}/edit")
def edit_profile_page(request: Request, username: str, session: Session = Depends(get_session)):
    if not request.headers.get("HX-Request"):
        return RedirectResponse(url=f"/user/{username}")
    user = get_user_by_name(session, username)
    user_info = {
        "username": user.username,
        "bio": user.bio
    }
    return render(request, "/partials/edit_profile.html", context={"user": user_info})


@app.get("/user/{username}/attempts")
def get_attempts(
    request: Request,
    username: str,
    offset: int = 0,
    session: Session = Depends(get_session)
):

    attempts = get_user_attempts(session, username, offset, ATTEMPT_PAGINATION_STEP)

    return templates.TemplateResponse(
        request,
        "partials/attempt_list.html",
        {
            "attempts": attempts,
            "next_offset": offset + ATTEMPT_PAGINATION_STEP,
            "username": username
        }
    )


@app.patch("/user/{username}/edit")
def edit_profile(request: Request, username: str, new_username: str = Form(...), new_bio: str = Form(...), session: Session = Depends(get_session)):
    user = get_user_by_name(session, username)

    username_error = valid_username(new_username)
    bio_error = valid_bio(new_bio)

    if username_error or bio_error:
        error_msg = username_error or bio_error
        return HTMLResponse(
            content=f'<p>{error_msg}</p>',
            headers={"HX-Retarget": ".error"} 
        )

    update_username(session, user, new_username)
    update_bio(session, user, new_bio)
    session.commit()
    user_info = user_dict(new_username, session)
    response = render(
        request,
        "/partials/default_user_info.html",
        context={"user": user_info, "active_username": new_username, "oob": True}
    )
    response.set_cookie(key="session_user", value=new_username)
    response.headers["HX-Push-Url"] = f'/user/{new_username}'
    return response


@app.delete("/user/{username}")
async def delete_user(username: str, session: Session = Depends(get_session), active_user: User = Depends(get_active_user)):
    if active_user.username != username:
        raise HTTPException(status_code=403, detail="You can only delete your own account")

    delete_user_by_name(session, username)
    session.commit()

    response = Response()
    response.headers["HX-Redirect"] = "/login"
    response.delete_cookie(key="session_user")
    return response