"""
This module contains the routes for the history API endpoints.

Functions:
- create_history: Create a new history in the database.
- get_all_histories: Retrieve all histories.
- get_history: Retrieve a history by ID.
- update_history: Update a history by ID.
- delete_history: Delete a history by ID.
"""
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status
from pera_fastapi.models.schemas import HistoryBase
from sqlalchemy.orm import Session
from pera_fastapi.models import models
from pera_fastapi.models.database import engine, get_db, SessionLocal
from fastapi_cache.decorator import cache
from sqlalchemy.future import select
from fastapi.responses import JSONResponse


DBD = Annotated[Session, Depends(get_db)]

router = APIRouter()

@router.post("/history/", status_code=status.HTTP_201_CREATED)
async def create_history(history: HistoryBase, db: DBD):
    """
    Create a new history in the database.

    Args:
        history (StatusAccount): The history data to be added.
        db (DBD): The database session.

    Returns:
        str: A success message.
    """
    db_history = models.History(**history.dict())
    db.add(db_history)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="An error occurred while committing the transaction.") from e
    return JSONResponse(content={"message": "Success add history"}, status_code=status.HTTP_201_CREATED)

@router.get("/histories/",status_code=status.HTTP_200_OK)
async def get_all_histories(db: DBD):
    """
    Retrieve all histories.

    Returns:
        List[models.History]: A list of all histories.
    
    Raises:
        HTTPException: If no histories are found.
    """
    select_history = select(models.History)
    result = await db.execute(select_history)
    histories = result.scalars().all()
    if not histories:
        raise HTTPException(status_code=404,detail='Histories was not found')
    return histories

@router.get("/history/{id_history}",status_code=status.HTTP_200_OK)
async def get_history(id_history: int, db: DBD):
    """
    Retrieve a history by ID.

    Args:
        id_history (int): The ID of the history to retrieve.
        db (DBD): The database dependency.

    Returns:
        The history with the specified ID.

    Raises:
        HTTPException: If the history with the specified ID is not found.
    """
    select_history = select(models.History).where(models.History.id == id_history)
    result = await db.execute(select_history)
    history = result.scalars().first()
    if not history:
        raise HTTPException(status_code=404,detail='History was not found')
    return history


@router.put("/history/{id_history}",status_code=status.HTTP_200_OK)
async def update_history(id_history: int, history: HistoryBase, db: DBD):
    """
    Update a history by ID.

    Args:
        id_history (int): The ID of the history to update.
        history (HistoryBase): The history data to be updated.
        db (DBD): The database dependency.

    Returns:
        The history with the specified ID.

    Raises:
        HTTPException: If the history with the specified ID is not found.
    """
    select_history = select(models.History).where(models.History.id == id_history)
    result = await db.execute(select_history)
    db_history = result.scalars().first()
    if db_history is None:
        raise HTTPException(status_code=404,detail='History was not found')
    update_history = models.History(**history.dict(), id=id_history)
    db.merge(update_history)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="An error occurred while committing the transaction.") from e
    return update_history


@router.delete("/history/{id_history}",status_code=status.HTTP_200_OK)
async def delete_history(id_history: int, db: DBD):
    """
    Delete a history by ID.

    Args:
        id_history (int): The ID of the history to delete.
        db (DBD): The database dependency.

    Returns:
        str: A success message.

    Raises:
        HTTPException: If the history with the specified ID is not found.
    """
    select_history = select(models.History).where(models.History.id == id_history)
    result = await db.execute(select_history)
    db_history = result.scalars().first()
    if db_history is None:
        raise HTTPException(status_code=404,detail='History was not found')
    db.delete(db_history)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="An error occurred while committing the transaction.") from e
    return JSONResponse(content={"message": "Success delete history"}, status_code=status.HTTP_200_OK)
    
@router.get("/history/{id_history}/group",status_code=status.HTTP_200_OK)
async def get_history_group(id_history: int, db: DBD):
    """
    Retrieve the group of an history by ID.

    Args:
        id_history (int): The ID of the history to retrieve.
        db (DBD): The database dependency.

    Returns:
        The group of the history with the specified ID.

    Raises:
        HTTPException: If the history with the specified ID is not found.
    """
    select_history = select(models.History).where(models.History.id == id_history)
    result = await db.execute(select_history)
    history = result.scalars().first()
    if not history:
        raise HTTPException(status_code=404,detail='History was not found')
    return history.group

@router.get("/history/{id_history}/account",status_code=status.HTTP_200_OK)
async def get_history_account(id_history: int, db: DBD):
    """
    Retrieve the account of an history by ID.

    Args:
        id_history (int): The ID of the history to retrieve.
        db (DBD): The database dependency.

    Returns:
        The account of the history with the specified ID.

    Raises:
        HTTPException: If the history with the specified ID is not found.
    """
    select_history = select(models.History).where(models.History.id == id_history)
    result = await db.execute(select_history)
    history = result.scalars().first()
    if not history:
        raise HTTPException(status_code=404,detail='History was not found')
    return history.account

@router.get("/history/{id_history}/group_senders",status_code=status.HTTP_200_OK)
async def get_history_group_senders(id_history: int, db: DBD):
    """
    Retrieve the group_senders of an history by ID.

    Args:
        id_history (int): The ID of the history to retrieve.
        db (DBD): The database dependency.

    Returns:
        The group_senders of the history with the specified ID.

    Raises:
        HTTPException: If the history with the specified ID is not found.
    """
    select_history = select(models.History).where(models.History.id == id_history)
    result = await db.execute(select_history)
    history = result.scalars().first()
    if not history:
        raise HTTPException(status_code=404,detail='History was not found')
    return history.group_senders
