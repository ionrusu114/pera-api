"""
This module contains the API routes for managing group senders.
"""

# FILEPATH: /home/ionrusu114api/htdocs/www.api.ionrusu114.me/pera-fastapi/pera_fastapi/routes/group_senders_router.py

from typing import Dict, List,Annotated
from fastapi import APIRouter, HTTPException, Depends, status
from pera_fastapi.models.schemas import Group_SendersBase,GroupsSendersSelectBase
from sqlalchemy.orm import Session
from pera_fastapi.models import models
from pera_fastapi.models.database import get_db
from sqlalchemy.future import select
from fastapi.responses import JSONResponse

DBD = Annotated[Session, Depends(get_db)]
router = APIRouter()

@router.post("/group_senders/", status_code=status.HTTP_201_CREATED)
async def create_group_senders(group_senders: GroupsSendersSelectBase, db: DBD):
    """
    Create a new group_senders in the database.

    Args:
        group_senders (Group_SendersBase): The group_senders data to be added.
        db (Session): The database session.

    Returns:
        Dict[str, Union[str, int]]: A success message and the ID of the created group_senders.
    """
    db_group_senders = models.Group_Senders(**group_senders.dict())
    db.add(db_group_senders)
    await db.commit()
    await db.refresh(db_group_senders)
    return {"message": "Success add group_senders", "id": db_group_senders.id}

@router.get("/group_senders/", status_code=status.HTTP_200_OK)
async def get_all_group_senders(db: DBD):
    """
    Retrieve all group_senders.

    Returns:
        List[models.Group_Senders]: A list of all group_senders.
    
    Raises:
        HTTPException: If no group_senders are found.
    """
    select_group_senders = select(models.Group_Senders)
    result = await db.execute(select_group_senders)
    group_senders = result.scalars().all()
    if not group_senders:
        raise HTTPException(status_code=404, detail='Group_senders was not found')
    return group_senders

@router.get("/group_senders/{id_group_senders}", status_code=status.HTTP_200_OK)
async def get_group_senders(id_group_senders: int, db: DBD):
    """
    Retrieve a group_senders by ID.

    Args:
        id_group_senders (int): The ID of the group_senders to retrieve.
        db (Session): The database dependency.

    Returns:
        The group_senders with the specified ID.

    Raises:
        HTTPException: If the group_senders with the specified ID is not found.
    """
    select_group_senders = select(models.Group_Senders).where(models.Group_Senders.id_group_senders == id_group_senders)
    result = await db.execute(select_group_senders)
    group_senders = result.scalars().first()
    if not group_senders:
        raise HTTPException(status_code=404, detail='Group_senders was not found')
    return group_senders
 

@router.put("/group_senders/{id_group_senders}", status_code=status.HTTP_200_OK)
async def update_group_senders(id_group_senders: int, group_senders: GroupsSendersSelectBase, db: DBD):
    """
    Update a group_senders.

    Args:
        id_group_senders (int): The ID of the group_senders to update.
        group_senders (Group_SendersBase): The group_senders data to be updated.
        db (Session): The database session.

    Returns:
        Dict[str, str]: A success message.

    Raises:
        HTTPException: If the group_senders with the specified ID is not found.
    """
    select_group_senders = select(models.Group_Senders).where(models.Group_Senders.id == id_group_senders)
    result = await db.execute(select_group_senders)
    db_group_senders = result.scalars().first()
    if not db_group_senders:
        raise HTTPException(status_code=404, detail='Group_senders was not found')
    update_group_senders = models.Group_Senders(**group_senders.dict(), id=id_group_senders)
    await db.merge(update_group_senders)
    await db.commit()
    return JSONResponse(content={"message": "Success update group_senders"}, status_code=status.HTTP_200_OK)
    

@router.delete("/group_senders/{id_group_senders}", status_code=status.HTTP_200_OK)
async def delete_group_senders(id_group_senders: int, db: DBD):
    """
    Delete a group_senders by ID.

    Args:
        id_group_senders (int): The ID of the group_senders to delete.
        db (Session): The database session.

    Returns:
        Dict[str, str]: A success message.

    Raises:
        HTTPException: If the group_senders with the specified ID is not found.
    """
    select_group_senders = select(models.Group_Senders).where(models.Group_Senders.id_group_senders == id_group_senders)
    result = await db.execute(select_group_senders)
    db_group_senders = result.scalars().first()
    if not db_group_senders:
        raise HTTPException(status_code=404, detail='Group_senders was not found')
    db.delete(db_group_senders)
    await db.commit()
    return JSONResponse(content={"message": "Success delete group_senders"}, status_code=status.HTTP_200_OK)

@router.get("/group_senders/account/{id_account}", status_code=status.HTTP_200_OK)
async def get_group_senders_by_account(id_account: int, db: DBD):
    """
    Retrieve all group_senders by account.

    Args:
        id_account (int): The ID of the account to retrieve.
        db (Session): The database dependency.

    Returns:
        List[models.Group_Senders]: A list of all group_senders by account.
    
    Raises:
        HTTPException: If no group_senders are found.
    """
    select_group_senders = select(models.Group_Senders).where(models.Group_Senders.id_account == id_account)
    result = await db.execute(select_group_senders)
    group_senders = result.scalars().all()
    if not group_senders:
        raise HTTPException(status_code=404, detail='Group_senders was not found')
    return group_senders
