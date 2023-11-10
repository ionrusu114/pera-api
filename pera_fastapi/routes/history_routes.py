from typing import Annotated
from fastapi import APIRouter, HTTPException,Depends,status
from pera_fastapi.models.schemas import HistoryBase
from sqlalchemy.orm import Session
from pera_fastapi.models import models
from pera_fastapi.models.database import engine, get_db,SesssionLocal


DBD = Annotated[Session, Depends(get_db)]

router = APIRouter()

@router.post("/history/",status_code=status.HTTP_201_CREATED)
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
    db.commit()
    return {"message": "Success add history","status":status.HTTP_201_CREATED}

@router.get("/histories/",status_code=status.HTTP_200_OK)
async def get_all_histories(db: DBD):
    """
    Retrieve all histories.

    Returns:
        List[models.History]: A list of all histories.
    
    Raises:
        HTTPException: If no histories are found.
    """
    histories = db.query(models.History).all()
    if histories is None:
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
    history = db.query(models.History).filter(models.History.id == id_history).first()
    if history is None:
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
    db_history = db.query(models.History).filter(models.History.id == id_history).first()
    if db_history is None:
        raise HTTPException(status_code=404,detail='History was not found')
    db_history.id_group = history.id_group
    db_history.id_account = history.id_account
    db_history.status = history.status
    db.commit()
    return db_history

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
    db_history = db.query(models.History).filter(models.History.id == id_history).first()
    if db_history is None:
        raise HTTPException(status_code=404,detail='History was not found')
    db.delete(db_history)
    db.commit()
    return {"message": "Success delete history", "status": status.HTTP_200_OK}







