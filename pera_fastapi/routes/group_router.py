"""  This module contains the group router.  """
from typing import Annotated
from fastapi import APIRouter, HTTPException,Depends,status
from pera_fastapi.models.schemas import GroupBase
from sqlalchemy.orm import Session
from pera_fastapi.models import models
from pera_fastapi.models.database import engine, get_db,SesssionLocal


DBD = Annotated[Session, Depends(get_db)]

router = APIRouter()


@router.post("/group/",status_code=status.HTTP_201_CREATED)
async def create_group(group: GroupBase, db: DBD):
    """
    Create a new group in the database.

    Args:
        group (GroupBase): The group data to be added.
        db (DBD): The database session.

    Returns:
        str: A success message.
    """
    db_group = models.Group(**group.dict())
    db.add(db_group)
    db.commit()
    return "Success add group"


@router.get("/groups/",status_code=status.HTTP_200_OK)
async def get_all_groups(db: DBD):
    """
    Retrieve all groups.

    Returns:
        List[models.Group]: A list of all groups.
    
    Raises:
        HTTPException: If no groups are found.
    """
    groups = db.query(models.Group).all()
    if groups is None:
        raise HTTPException(status_code=404,detail='Groups was not found')
    return groups

@router.get("/group/{id_group}",status_code=status.HTTP_200_OK)
async def get_group(id_group: int, db: DBD):
    """
    Retrieve a group by ID.

    Args:
        id_group (int): The ID of the group to retrieve.
        db (DBD): The database dependency.

    Returns:
        The group with the specified ID.

    Raises:
        HTTPException: If the group with the specified ID is not found.
    """
    group = db.query(models.Group).filter(models.Group.id == id_group).first()
    if group is None:
        raise HTTPException(status_code=404,detail='Group was not found')
    return group


@router.delete("/group/{id_group}",status_code=status.HTTP_200_OK)
async def delete_group(id_group: int, db: DBD):
    """
    Deletes a group with the given id from the database.

    Args:
    - id_group (int): The id of the group to be deleted.
    - db (DBD): The database session dependency.

    Returns:
    - str: A success message indicating the id of the deleted group.
    
    Raises:
    - HTTPException: If the group with the given id is not found in the database.
    """
    db_group = db.query(models.Group).filter(models.Group.id == id_group).first()
    if db_group is None:
        raise HTTPException(status_code=404,detail='Group was not found')
    db.delete(db_group)
    db.commit()
    return "Success delete group - {}".format(id_group)

@router.put("/group/{id_group}",status_code=status.HTTP_200_OK)
async def update_group(id_group: int, group: GroupBase, db: DBD):
    """
    Updates a group with the given id in the database.

    Args:
    - id_group (int): The id of the group to be updated.
    - group (GroupBase): The group data to be updated.
    - db (DBD): The database session dependency.

    Returns:
    - str: A success message indicating the id of the updated group.
    
    Raises:
    - HTTPException: If the group with the given id is not found in the database.
    """
    db_group = db.query(models.Group).filter(models.Group.id == id_group).first()
    if db_group is None:
        raise HTTPException(status_code=404,detail='Group was not found')
    db_group.name = group.name
    db_group.category = group.category
    db.commit()
    return "Success update group - {}".format(id_group)