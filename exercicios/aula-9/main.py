from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, create_engine, Session, select, col
from contextlib import asynccontextmanager
from typing import Optional
from models import Aluno

@asynccontextmanager
async def initFunction(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=initFunction)

arquivo_sqlite = "aula9.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite)

templates = Jinja2Templates(directory=["templates"])

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def buscar_alunos(busca: str = '', page: int = 1, per_page: int = 10):
    with Session(engine) as session:
        offset = (page - 1) * per_page
        query = select(Aluno).where(col(Aluno.nome).contains(busca)).order_by(Aluno.nome).offset(offset).limit(per_page)
        return session.exec(query).all()

@app.get("/", response_class=HTMLResponse)
def busca(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/lista", response_class=HTMLResponse)
def lista(request: Request, busca: str | None = '', page: int = 1, per_page: int = 10):
    alunos = buscar_alunos(busca, page, per_page)
    has_next = len(alunos) == per_page
    has_prev = page > 1
    return templates.TemplateResponse(request, "lista.html", {"alunos": alunos, "busca": busca, "page": page, "has_next": has_next, "has_prev": has_prev})

@app.get("/editarAlunos", response_class=HTMLResponse)
def novoAluno(request: Request):
    return templates.TemplateResponse(request, "options.html")

@app.post("/novoAluno", response_class=HTMLResponse)
def criar_aluno(nome: str = Form(...)):
    with Session(engine) as session:
        novo_aluno = Aluno(nome=nome)
        session.add(novo_aluno)
        session.commit()
        session.refresh(novo_aluno)
        return HTMLResponse(content=f"<p>O(a) aluno(a) {novo_aluno.nome} foi registrado(a)!</p>")

@app.delete("/deletaAluno", response_class=HTMLResponse)
def deletar_aluno(id: int):
    with Session(engine) as session:
        query = select(Aluno).where(Aluno.id == id)
        aluno = session.exec(query).first()
        if not aluno:
            raise HTTPException(404, "Aluno não encontrado")
        session.delete(aluno)
        session.commit()
        return HTMLResponse(content=f"<p>O(a) aluno(a) {aluno.nome} foi deletado(a)!</p>")

@app.put("/atualizaAluno", response_class=HTMLResponse)
def atualizar_aluno(id: int = Form(...), novoNome: str = Form(...)):
    with Session(engine) as session:
        query = select(Aluno).where(Aluno.id == id)
        aluno = session.exec(query).first()
        if not aluno:
            raise HTTPException(404, "Aluno não encontrado")
        nomeAntigo = aluno.nome
        aluno.nome = novoNome
        session.commit()
        session.refresh(aluno)
        return HTMLResponse(content=f"<p>O(a) aluno(a) {nomeAntigo} foi atualizado(a) para {aluno.nome}!</p>")