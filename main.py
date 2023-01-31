from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from routes.routes import routes

app = FastAPI()
app.include_router(routes)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/img", StaticFiles(directory="img"), name="img")
app.mount("/audio", StaticFiles(directory="audio"), name="audio")
templates = Jinja2Templates(directory="templates")








