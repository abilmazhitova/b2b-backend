from fastapi import FastAPI

from app.api import auth
from app.api import telecom
app = FastAPI(title="Coworking Analyzer API")



app.include_router(auth.router)
app.include_router(telecom.router)