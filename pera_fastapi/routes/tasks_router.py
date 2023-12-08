""" This module contains the routes for the tasks. """

from typing import Dict, List, Annotated
from fastapi import APIRouter, HTTPException, Depends, status,WebSocket
from pera_fastapi.models.schemas import TasksBase, TasksUpdateBase,TaskUpdateStatusBase
from sqlalchemy.orm import Session
from pera_fastapi.models import models
from pera_fastapi.models.database import get_db
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from datetime import datetime

DBD = Annotated[Session, Depends(get_db)]
router = APIRouter()

@router.post("/task/", status_code=status.HTTP_201_CREATED)
async def create_task(task: TasksBase, db: DBD):
    """
    Create a new task.
    
    Args:
        task (TasksBase): The task data to be created.
        db (Session): The database session.
    
    Returns:
        Dict[str, str]: A success message.
    """
    try:
        db_task = models.Tasks(**task.dict())
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        return JSONResponse(content={"message": "Success create task", "id": db_task.id}, status_code=status.HTTP_201_CREATED)
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')

@router.get("/tasks/", status_code=status.HTTP_200_OK)
async def get_all_tasks(db: DBD):
    try:
        select_tasks = select(models.Tasks)
        result = await db.execute(select_tasks)
        tasks = result.scalars().all()
        if not tasks:
            raise HTTPException(status_code=404, detail='Tasks was not found')
        return tasks
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')

@router.get("/tasks/count", status_code=status.HTTP_200_OK)
async def get_all_tasks_count(db: DBD):
    try:
        select_tasks = select(models.Tasks)
        result = await db.execute(select_tasks)
        tasks = result.scalars().all()
        if not tasks:
            raise HTTPException(status_code=404, detail='Tasks was not found')
        return len(tasks)
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')

@router.get("/tasks/{page}/{perPage}", status_code=status.HTTP_200_OK)
async def get_all_tasks_paginate(page: int, perPage: int, db: DBD):
    try:
        select_tasks = select(models.Tasks).order_by(models.Tasks.id.desc())
        result = await db.execute(select_tasks.offset((page - 1) * perPage).limit(perPage))
        tasks = result.scalars().all()
        if not tasks:
            raise HTTPException(status_code=404, detail='Tasks was not found')
        return tasks
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')

@router.get("/task/{id_task}", status_code=status.HTTP_200_OK)
async def get_task(id_task: int, db: DBD):
    try:
        select_task = select(models.Tasks).where(models.Tasks.id == id_task)
        result = await db.execute(select_task)
        group_task = result.scalars().first()
        if not group_task:
            raise HTTPException(status_code=404, detail='Task was not found')
        return group_task
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')

@router.get("/task/{id_group_sender}/group_sender", status_code=status.HTTP_200_OK)
async def get_task_by_group_sender(id_group_sender: int, db: DBD):
    """ Get all tasks by group sender id """
    try:
        select_task = select(models.Tasks).where(models.Tasks.id_group_sender == id_group_sender)
        result = await db.execute(select_task)
        group_task = result.scalars().first()
        if not group_task:
            raise HTTPException(status_code=404, detail='Task was not found')
        return group_task.task_id
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')


@router.put("/tasks/{id}", status_code=status.HTTP_200_OK)
async def update_task(id: int, task: TasksUpdateBase, db: DBD):
    try:
        select_task = select(models.Tasks).where(models.Tasks.id == id)
        result = await db.execute(select_task)
        db_task = result.scalars().first()
        if not db_task:
            raise HTTPException(status_code=404, detail='Group_senders was not found')
        update_task = models.Tasks(**task.dict(), id=id)
        await db.merge(update_task)
        await db.commit()
        return JSONResponse(content={"message": "Success update task"}, status_code=status.HTTP_200_OK)
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')
    

@router.put("/task/{task_id}/worker", status_code=status.HTTP_200_OK)
async def update_task_work(task_id: str, task_update: TaskUpdateStatusBase, db: DBD):
    try:
        select_task = select(models.Tasks).where(models.Tasks.task_id == task_id)
        result = await db.execute(select_task)
        db_task = result.scalars().first()
        if not db_task:
            raise HTTPException(status_code=404, detail='Task was not found')
        db_task.stopped_at = datetime.now()
        db_task.status = task_update.status
        await db.commit()
        return JSONResponse(content={"message": "Success update task"}, status_code=status.HTTP_200_OK)
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')

@router.delete("/task/{id}", status_code=status.HTTP_200_OK)
async def delete_Task(id: int, db: DBD):
    try:
        select_task = select(models.Tasks).where(models.Tasks.id == id)
        result = await db.execute(select_task)
        db_task = result.scalars().first()
        if not db_task:
            raise HTTPException(status_code=404, detail='Task was not found')
        db.delete(db_task)
        await db.commit()
        return JSONResponse(content={"message": "Success delete task"}, status_code=status.HTTP_200_OK)
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')
