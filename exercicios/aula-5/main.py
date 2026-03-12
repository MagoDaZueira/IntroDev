from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()

templates = Jinja2Templates(directory="templates")

class User(BaseModel):
    nome: str
    bio: str
    senha: str

users: list[User] = []


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="cadastro.html"
    )


@app.post("/users")
def create_user(user: User):
    users.append(user)


@app.get("/login")
def login_render(request: Request):
    return templates.TemplateResponse(
        request=request, name="login.html"
    )
