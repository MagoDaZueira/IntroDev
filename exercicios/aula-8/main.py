from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory=["templates"])

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