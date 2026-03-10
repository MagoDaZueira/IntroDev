from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
	nome: str
	idade: int

users = []


@app.get("/")
def read_root():
	return FileResponse("./index.html")


@app.post("/users") # Adiciona um usuário numa lista
async def create_user(user : User):
	users.append(user)


@app.get("/users") # Lê todos os usuários da lista ou um índice específico (usando query parameter)
async def get_users(index : int | None = None):
	if index is None:
		return users
	if index < 0 or index >= len(users):
		return {"Não existe um usuário com esse índice"}
	return users[index]


@app.delete("/users") # Limpa a lista de usuários
async def delete():
	users.clear()