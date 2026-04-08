from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

templates = Jinja2Templates(directory=["templates"])
app.mount("/static", StaticFiles(directory="static"), name="static")

curtidas = 0

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html", {"curtidas": curtidas})

@app.post("/curtir")
async def curtir(request: Request):
    global curtidas
    curtidas += 1
    return templates.TemplateResponse(request, "partials/contador.html", {"curtidas": curtidas})

@app.delete("/curtir")
async def curtir(request: Request):
    global curtidas
    curtidas = 0
    return templates.TemplateResponse(request, "partials/contador.html", {"curtidas": curtidas})

@app.get("/curtidas", response_class=HTMLResponse)
async def get_curtidas(request: Request):
    return templates.TemplateResponse(request, "curtidas.html", {"curtidas": curtidas})

@app.get("/jupiter", response_class=HTMLResponse)
async def get_jupiter(request: Request):
    return templates.TemplateResponse(request, "aula-1/jupiter/index.html")

@app.get("/professor", response_class=HTMLResponse)
async def get_professor(request: Request):
    return templates.TemplateResponse(request, "aula-1/site-professor/index.html")

@app.get("/research", response_class=HTMLResponse)
async def get_research(request: Request):
    return templates.TemplateResponse(request, "aula-1/site-professor/research.html")

@app.get("/students", response_class=HTMLResponse)
async def get_students(request: Request):
    return templates.TemplateResponse(request, "aula-1/site-professor/students.html")

@app.get("/contact", response_class=HTMLResponse)
async def get_contact(request: Request):
    return templates.TemplateResponse(request, "aula-1/site-professor/contact.html")