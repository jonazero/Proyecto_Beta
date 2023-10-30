from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from routes.routes import routes
from fastapi.middleware.cors import CORSMiddleware
from auth import auth_app
app = FastAPI()

origins = [
    "http://localhost:8000",
    "http://localhost:8000/signup",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/auth", auth_app)
app.include_router(routes)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
