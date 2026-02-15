from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .db import Base
from .db import engine
from . import models
from .routes import router


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
Base.metadata.create_all(bind=engine)
app.include_router(router)
