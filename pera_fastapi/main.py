"""
This module contains the main application and API endpoints.

The module initializes the FastAPI application and defines the API endpoints for the PERA API.
It also configures the Cross-Origin Resource Sharing (CORS) middleware to allow requests from any origin.
"""

from typing import Annotated
from fastapi import FastAPI, HTTPException,Depends,status,Request
from fastapi_users import FastAPIUsers
from sqlalchemy.orm import Session
from .models import models
from .models.database import engine, get_db
from .routes import account_router,group_router,history_routes,group_senders_router
from fastapi.middleware.cors import CORSMiddleware

from .auth.auth import auth_backend
from .auth.database import User
from .auth.manager import get_user_manager
from .auth.schemas import UserCreate, UserRead

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from fastapi.responses import JSONResponse
from .settings import settings


from .tasks.router import router as router_tasks

# models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="PERA API",name="Pera API",version="1.0.0",description="Pera API Using FastAPI",docs_url="/docs/")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# Configuration CORS
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

app.include_router(group_router.router, prefix="/api/telegram", tags=["groups"])
app.include_router(account_router.router, prefix="/api/telegram", tags=["accounts"])
app.include_router(history_routes.router, prefix="/api/telegram", tags=["histories"])
app.include_router(group_senders_router.router, prefix="/api/telegram", tags=["group_senders"])

app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_auth_router(auth_backend, requires_verification=False), prefix="/auth/jwt", tags=["auth"])



current_user = fastapi_users.current_user()

app.include_router(
    router_tasks,
    dependencies=[Depends(current_user)]
    )
@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.username}"

@app.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anonym"

@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url(f"redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/0", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")