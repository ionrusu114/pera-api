""" 
This module contains the group router.

The group router provides the following endpoints:
- POST /group/ - creates a new group in the database.
- GET /groups/ - retrieves all groups.
- GET /group/{id_group} - retrieves a group by ID.
- DELETE /group/{id_group} - deletes a group with the given id from the database.
- PUT /group/{id_group} - updates a group with the given id in the database.
"""
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status
from pera_fastapi.models.schemas import GroupBase
from sqlalchemy.orm import Session
from pera_fastapi.models import models
from pera_fastapi.models.database import engine, get_db, SessionLocal
from fastapi_cache.decorator import cache
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

DBD = Annotated[Session, Depends(get_db)]

router = APIRouter()


@router.post("/group/", status_code=status.HTTP_201_CREATED)
async def create_group(group: GroupBase, db: DBD):
    """
    Create a new group in the database.

    Args:
        group (GroupBase): The group data to be added.
        db (DBD): The database session.

    Returns:
        str: A success message.

    Raises:
        HTTPException: If there is an integrity error.
    """
    try:
        db_group = models.Group(**group.dict())
        db.add(db_group)
        await db.commit()
        return "Success add group"
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Integrity error")


@router.get("/groups/", status_code=status.HTTP_200_OK)
async def get_all_groups(db: DBD):
    """
    Retrieve all groups.

    Returns:
        List[models.Group]: A list of all groups.

    Raises:
        HTTPException: If no groups are found.
    """
    select_group = select(models.Group)
    result = await db.execute(select_group)
    groups = result.scalars().all()
    if not groups:
        raise HTTPException(status_code=404, detail='Groups was not found')
    return groups

@router.get("/groups/{page}/{perPage}", status_code=status.HTTP_200_OK)
async def get_all_groups_paginate(page: int, perPage: int, db: DBD):
    """
    Retrieve all groups.

    Returns:
        List[models.Group]: A list of all groups.

    Raises:
        HTTPException: If no groups are found.
    """
    select_group = select(models.Group).limit(perPage).offset((page-1)*perPage)
    result = await db.execute(select_group)
    groups = result.scalars().all()
    if not groups:
        raise HTTPException(status_code=404, detail='Groups was not found')
    return groups

@router.get("/groups/count", status_code=status.HTTP_200_OK)
async def get_all_groups_count(db: DBD):
    """
    Retrieve all groups.

    Returns:
        List[models.Group]: A list of all groups.

    Raises:
        HTTPException: If no groups are found.
    """
    select_group = select(models.Group)
    result = await db.execute(select_group)
    groups = result.scalars().all()
    if not groups:
        raise HTTPException(status_code=404, detail='Groups was not found')
    return len(groups)

@router.get("/group/{id_group}", status_code=status.HTTP_200_OK)
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
    select_group = select(models.Group).where(models.Group.id == id_group)
    result = await db.execute(select_group)
    group = result.scalars().first()
    if not group:
        raise HTTPException(status_code=404, detail='Group was not found')
    return group


@router.delete("/group/{id_group}", status_code=status.HTTP_200_OK)
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
    stmt_group = select(models.Group).where(models.Group.id == id_group)
    result_group = await db.execute(stmt_group)
    group = result_group.scalars().first()
    if not group:
        raise HTTPException(status_code=404, detail='Group was not found')
    await db.delete(group)
    await db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Success delete group"})


@router.put("/group/{id_group}", status_code=status.HTTP_200_OK)
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

    Example:
    ```
    # Update group with id 1
    response = await client.put("/group/1", json={"name": "New Group Name"})
    assert response.status_code == 200
    assert response.json() == {"message": "Success update group"}
    ```
    """
    try:
        select_stmt = select(models.Group).where(models.Group.id == id_group)
        result = await db.execute(select_stmt)
        db_group = result.scalars().first()
        if not db_group:
            raise HTTPException(status_code=404, detail='Group was not found')
        update_group = models.Group(**group.dict(), id=id_group)
        await db.merge(update_group)
        await db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Success update group"})
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Integrity error")
