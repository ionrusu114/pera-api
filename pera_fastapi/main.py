""" This module contains the main application and API endpoints."""
from typing import Annotated
from fastapi import FastAPI, HTTPException,Depends,status
from sqlalchemy.orm import Session
from .models import models
from .models.database import engine, get_db,SesssionLocal
from .routes import account_router,group_router,history_routes,group_senders_router
from fastapi.middleware.cors import CORSMiddleware




models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="PERA API",name="Pera API",version="1.0.0",description="Pera API Using FastAPI",docs_url="/docs/")

# Configurarea CORS
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(group_router.router, prefix="/api/telegram/bot", tags=["groups"])
app.include_router(account_router.router, prefix="/api/telegram/bot", tags=["accounts"])
app.include_router(history_routes.router, prefix="/api/telegram/bot", tags=["histories"])
app.include_router(group_senders_router.router, prefix="/api/telegram/bot", tags=["group_senders"])
