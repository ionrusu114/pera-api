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
from .routes import account_router,group_router,history_routes,group_senders_router,tasks_router
from fastapi.middleware.cors import CORSMiddleware

from .auth_v2.db import User, create_db_and_tables
from .auth_v2.schemas import UserCreate, UserRead, UserUpdate
from .auth_v2.users import jwt_auth_backend, cookie_auth_backend, current_active_user, fastapi_users


from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from fastapi.responses import JSONResponse
from .settings import settings
from fastapi.responses import Response
# from .security import get_api_key
# from fastapi import Security

from .tasks.router import router as router_tasks

app = FastAPI(title="PERA API",name="Pera API",version="1.0.0",description="Pera API Using FastAPI",docs_url="/docs/")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

# Configuration CORS
origins = [
    # "localhost:5173",
    # "localhost:3000",
    # "localhost:3001",
    # "localhost:4173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    fastapi_users.get_auth_router(cookie_auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}

app.include_router(group_router.router, prefix="/api/telegram", tags=["groups"])
app.include_router(account_router.router, prefix="/api/telegram", tags=["accounts"])
app.include_router(history_routes.router, prefix="/api/telegram", tags=["histories"])
app.include_router(group_senders_router.router, prefix="/api/telegram", tags=["group_senders"])

app.include_router(
    router_tasks, prefix="/tasks",
    tags=["tasks"],
    # dependencies=[Depends(current_active_user)]
    )
app.include_router(
    tasks_router.router, prefix="/tasks",
    tags=["tasks"],
    # dependencies=[Depends(current_active_user)]
    )

@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url(f"redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/0", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")