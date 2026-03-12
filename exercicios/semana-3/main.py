from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
	nome: str
	idade: int

users = []


@app.get("/")
def read_root():
	return FileResponse("./index.html")


@app.post("/users", response_class=PlainTextResponse) # Adiciona um usuário numa lista
async def create_user(user : User):
	users.append(user)
	return f"Novo usuário: {user.nome}, {user.idade} anos"


@app.get("/users", response_class=PlainTextResponse) # Lê todos os usuários da lista ou um índice específico (usando query parameter)
async def get_users(index : int | None = None):
	if (len(users) == 0):
		return "Não existem usuários cadastrados"

	if index is None:
		return "Todos os usuários:\n-> " + "\n-> ".join(
			f"{user.nome}, {user.idade} anos"
			for user in users
		)

	if index < 0 or index >= len(users):
		return "Não existe um usuário com esse índice"

	return f"Usuário de índice {index}: {users[index].nome}, {users[index].idade} anos"


@app.delete("/users", response_class=PlainTextResponse) # Limpa a lista de usuários
async def delete():
	users.clear()
	return "Usuários deletados"