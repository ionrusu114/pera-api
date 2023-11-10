from typing import Annotated
from fastapi import APIRouter, HTTPException,Depends,status
from pera_fastapi.models.schemas import Group_SendersBase
from sqlalchemy.orm import Session
from pera_fastapi.models import models
from pera_fastapi.models.database import engine, get_db,SesssionLocal


DBD = Annotated[Session, Depends(get_db)]

router = APIRouter()

@router.post("/group_senders/",status_code=status.HTTP_201_CREATED)
async def create_group_senders(group_senders: Group_SendersBase, db: DBD):
    """
    Create a new group_senders in the database.

    Args:
        group_senders (Group_SendersBase): The group_senders data to be added.
        db (DBD): The database session.

    Returns:
        str: A success message.
    """
    db_group_senders = models.Group_Senders(**group_senders.dict())
    db.add(db_group_senders)
    db.commit()
    return { "message": "Success add group_senders","status":status.HTTP_201_CREATED}

@router.get("/group_senders/",status_code=status.HTTP_200_OK)
async def get_all_group_senders(db: DBD):
    """
    Retrieve all group_senders.

    Returns:
        List[models.Group_Senders]: A list of all group_senders.
    
    Raises:
        HTTPException: If no group_senders are found.
    """
    group_senders = db.query(models.Group_Senders).all()
    if group_senders is None:
        raise HTTPException(status_code=404,detail='Group_senders was not found')
    return group_senders

@router.get("/group_senders/{id_group_senders}",status_code=status.HTTP_200_OK)
async def get_group_senders(id_group_senders: int, db: DBD):
    """
    Retrieve a group_senders by ID.

    Args:
        id_group_senders (int): The ID of the group_senders to retrieve.
        db (DBD): The database dependency.

    Returns:
        The group_senders with the specified ID.

    Raises:
        HTTPException: If the group_senders with the specified ID is not found.
    """
    group_senders = db.query(models.Group_Senders).filter(models.Group_Senders.id_group_senders == id_group_senders).first()
    if group_senders is None:
        raise HTTPException(status_code=404,detail='Group_senders was not found')
    return group_senders

@router.put("/group_senders/{id_group_senders}",status_code=status.HTTP_200_OK)
async def update_group_senders(id_group_senders: int, group_senders: Group_SendersBase, db: DBD):
    """
    Update a group_senders.

    Args:
        id_group_senders (int): The ID of the group_senders to update.
        group_senders (Group_SendersBase): The group_senders data to be updated.
        db (DBD): The database session.

    Returns:
        str: A success message.

    Raises:
        HTTPException: If the group_senders with the specified ID is not found.
    """
    db_group_senders = db.query(models.Group_Senders).filter(models.Group_Senders.id_group_senders == id_group_senders).first()
    if db_group_senders is None:
        raise HTTPException(status_code=404,detail='Group_senders was not found')
    db_group_senders.id_account = group_senders.id_account
    db_group_senders.group_list = group_senders.group_list
    db.commit()
    return { "message": "Success update group_senders","status":status.HTTP_200_OK}

@router.delete("/group_senders/{id_group_senders}",status_code=status.HTTP_200_OK)
async def delete_group_senders(id_group_senders: int, db: DBD):
    """
    Delete a group_senders by ID.

    Args:
        id_group_senders (int): The ID of the group_senders to delete.
        db (DBD): The database session.

    Returns:
        str: A success message.

    Raises:
        HTTPException: If the group_senders with the specified ID is not found.
    """
    db_group_senders = db.query(models.Group_Senders).filter(models.Group_Senders.id_group_senders == id_group_senders).first()
    if db_group_senders is None:
        raise HTTPException(status_code=404,detail='Group_senders was not found')
    db.delete(db_group_senders)
    db.commit()
    return { "message": "Success delete group_senders","status":status.HTTP_200_OK}

@router.get("/group_senders/account/{id_account}",status_code=status.HTTP_200_OK)
async def get_group_senders_by_account(id_account: int, db: DBD):
    """
    Retrieve all group_senders by account.

    Args:
        id_account (int): The ID of the account to retrieve.
        db (DBD): The database dependency.

    Returns:
        List[models.Group_Senders]: A list of all group_senders by account.
    
    Raises:
        HTTPException: If no group_senders are found.
    """
    group_senders = db.query(models.Group_Senders).filter(models.Group_Senders.id_account == id_account).all()
    if group_senders is None:
        raise HTTPException(status_code=404,detail='Group_senders was not found')
    return group_senders



