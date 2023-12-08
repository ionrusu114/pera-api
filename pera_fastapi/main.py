"""
This module contains the main application and API endpoints.

The module initializes the FastAPI application and defines the API endpoints for the PERA API.
It also configures the Cross-Origin Resource Sharing (CORS) middleware to allow requests from any origin.
"""

from typing import Annotated,List
from fastapi import FastAPI, HTTPException,Depends,status,Request,WebSocket,WebSocketDisconnect
from fastapi_users import FastAPIUsers
from sqlalchemy.orm import Session
from .models import models
from .models.database import engine, get_db
from .routes import account_router,group_router,history_routes,group_senders_router,tasks_router
from fastapi.middleware.cors import CORSMiddleware

from .auth.db import User, create_db_and_tables
from .auth.schemas import UserCreate, UserRead, UserUpdate
from .auth.users import jwt_auth_backend, cookie_auth_backend, current_active_user, fastapi_users

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from fastapi.responses import JSONResponse
from .settings import settings
from fastapi.responses import Response
import json
from sqlalchemy.future import select
from sqlalchemy import event
from sqlalchemy import func,desc
import asyncio
from concurrent.futures import ThreadPoolExecutor
from .tasks.router import router as router_tasks


DBD = Annotated[Session, Depends(get_db)]
app = FastAPI(title="PERA API",name="Pera API",version="1.0.0",description="Pera API Using FastAPI",docs_url="/docs/")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

# Configuration CORS
origins = [
    "http://localhost:3011",
    "https://www.pera.ionrusu114.me",
    "https://www.api.ionrusu114.me",
    # "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    fastapi_users.get_auth_router(jwt_auth_backend), prefix="/auth/jwt", tags=["auth"]
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
    return user.email

app.include_router(
    group_router.router, 
    prefix="/api/telegram", 
    tags=["groups"], 
    dependencies=[Depends(current_active_user)])

app.include_router(
    account_router.router, 
    prefix="/api/telegram", 
    tags=["accounts"],
    )

app.include_router(
    history_routes.router, 
    prefix="/api/telegram", 
    tags=["histories"],
    # dependencies=[Depends(current_active_user)]
    )

app.include_router(
    group_senders_router.router, 
    prefix="/api/telegram", 
    tags=["group_senders"],
    # dependencies=[Depends(current_active_user)]
    )

app.include_router(
    router_tasks, prefix="/tasks",
    tags=["tasks"],
    dependencies=[Depends(current_active_user)]
    )

app.include_router(
    tasks_router.router, prefix="/tasks",
    tags=["tasks"],
    # dependencies=[Depends(current_active_user)]
    )

 # Websocket Task List section
def task_to_dict(task):
    return {
        'id': task.id,
        'status': task.status,
        'updated_at': task.updated_at.isoformat() if task.updated_at else None,
        'created_at': task.created_at.isoformat() if task.created_at else None,
        'stopped_at': task.stopped_at.isoformat() if task.stopped_at else None,
        'task_id': task.task_id,
        'id_group_sender': task.id_group_sender,
    }

active_connections: List[WebSocket] = []

# Websocket
@app.websocket("/ws/tasks/")
async def websocket_endpoint(websocket: WebSocket, db: DBD):
    await websocket.accept()
    # Add the websocket connection to the list of active connections
    active_connections.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)

            if not isinstance(data_json, dict):
                await websocket.send_text("Invalid data format. Expected a JSON object.")
                continue

            pag = data_json.get('pag')
            per_page = data_json.get('per_page')

            if not isinstance(pag, int) or pag < 1:
                await websocket.send_text("Invalid 'pag' value. Expected a positive integer.")
                continue

            if per_page is None:
                per_page = 10
            elif not isinstance(per_page, int) or per_page < 1:
                await websocket.send_text("Invalid 'per_page' value. Expected a positive integer.")
                continue

            select_task = select(models.Tasks).order_by(desc(models.Tasks.id))

            result = await db.execute(select_task.offset((pag - 1) * per_page).limit(per_page))
            task_data = result.scalars().all()

            if not task_data:
                await websocket.close(code=1000)
                return

            task_data_dict = [task_to_dict(task) for task in task_data]
            await websocket.send_json(task_data_dict)

    except WebSocketDisconnect:
        # Remove the websocket connection from the list of active connections
        active_connections.remove(websocket)

executor = ThreadPoolExecutor()

# Function to broadcast a message to all active connections
async def broadcast_message(message: str):
    for connection in active_connections:
        await connection.send_text(message)

# Function to call when a new task is created
def on_new_task(mapper, connection, state):
    task = state  # Get the newly created task
    task_data_dict = task_to_dict(task)
    message = json.dumps(task_data_dict)

    def send_message():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(broadcast_message(message))
        loop.close()

    executor.submit(send_message)

# Register the event listener
event.listen(models.Tasks, 'after_insert', on_new_task)
event.listen(models.Tasks, 'after_update', on_new_task)

@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url(f"redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/0", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")