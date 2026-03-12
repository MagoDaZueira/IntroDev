from fastapi import FastAPI, Depends, Request, HTTPException, status, Cookie, Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Annotated

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


@app.post("/login")
def login(user: User, response: Response):
    usuario_encontrado = None
    for u in users:
        if u.nome == user.nome:
            usuario_encontrado = u
            break

    if not usuario_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não Encontrado")
    
    if user.senha != usuario_encontrado.senha:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Senha Incorreta")

    response.set_cookie(key="session_user", value=usuario_encontrado.nome)
    return {"message": "Logado com sucesso"}


def get_active_user(session_user: Annotated[str | None, Cookie()] = None):
    if not session_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Você não está logado"
        )

    user = next((u for u in users if u.nome == session_user), None)
    if not user:
        raise HTTPException(status_code=401, detail="Sessão inválida")

    return user


@app.get("/home")
def home_render(request: Request, user: User = Depends(get_active_user)):
    return templates.TemplateResponse(
        request=request, name="home.html", context={"user": user}
    )
