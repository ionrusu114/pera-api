"""
This module contains the API routes for managing accounts.

The routes include:
- Creating a new account
- Retrieving all accounts
- Retrieving an account by ID
- Updating an account
- Deleting an account

All routes require a database session dependency.
"""
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status
from pera_fastapi.models.schemas import AccountBase, StatusAccount, AccountBase
from sqlalchemy.orm import Session
from pera_fastapi.models import models
from pera_fastapi.models.database import engine, get_db, SessionLocal
from fastapi_cache.decorator import cache
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
import logging

DBD = Annotated[Session, Depends(get_db)]

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/account/", status_code=status.HTTP_201_CREATED)
async def create_account(account: AccountBase, db: DBD):
    """
    Create a new account in the database.

    Args:
        account (models.Account): The account data to be added.
        db (DBD): The database session.

    Returns:
        str: A success message.
    """
    try:
        db_account = models.Account(**account.dict())
        try:
            db.add(db_account)
            await db.commit()
            return JSONResponse(content={"message": "Success add account"}, status_code=status.HTTP_201_CREATED)
        except IntegrityError:
            await db.rollback()
            return JSONResponse(content={"message": "Account with this phone number already exists"}, status_code=status.HTTP_400_BAD_REQUEST)
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')

@router.get("/accounts/", status_code=status.HTTP_200_OK)
async def get_all_accounts(db: DBD):
    """
    Retrieve all accounts.

    Returns:
        List[models.Account]: A list of all accounts.

    Raises:
        HTTPException: If no accounts are found.
    """
    try:
        select_account = select(models.Account)
        result = await db.execute(select_account)
        accounts = result.scalars().all()
        if not accounts:
            raise HTTPException(status_code=404, detail='Accounts was not found')
        return accounts
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')

@router.get("/account/{id_account}", status_code=status.HTTP_200_OK)
async def get_account(id_account: int, db: DBD):
    """
    Retrieve an account by ID.

    Args:
        id_account (int): The ID of the account to retrieve.
        db (DBD): The database dependency.

    Returns:
        The account with the specified ID.

    Raises:
        HTTPException: If the account with the specified ID is not found.
    """
    try:
        select_account = select(models.Account).where(models.Account.id == id_account)
        result = await db.execute(select_account)
        account = result.scalars().first()
        if not account:
            raise HTTPException(status_code=404, detail='Account was not found')

        logger.info(f"Account data: {account}")
        return account
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')

@router.put("/account/{id_account}", status_code=status.HTTP_200_OK)
async def update_account(id_account: int, account: AccountBase, db: DBD):
    """
    Update an account in the database.

    Args:
        id_account (int): The ID of the account to update.
        account (StatusAccount): The account data to be updated.
        db (DBD): The database session.

    Returns:
        str: A success message.

    Raises:
        HTTPException: If the account with the specified ID is not found.
    """
    try:
        select_account = select(models.Account).where(models.Account.id == id_account)
        result = await db.execute(select_account)
        db_account = result.scalars().first()
        if db_account is None:
            raise HTTPException(status_code=404, detail='Account was not found')
        update_account = models.Account(**account.dict(), id=id_account)
        await db.merge(update_account)
        await db.commit()
        return JSONResponse(content={"message": "Success update account"}, status_code=status.HTTP_200_OK)
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')

@router.patch("/account/{id_account}", status_code=status.HTTP_200_OK)
async def update_account_status(id_account: int, account: StatusAccount, db: DBD):
    try:
        select_account = select(models.Account).where(models.Account.id == id_account)
        result = await db.execute(select_account)
        db_account = result.scalars().first()
        if db_account is None:
            raise HTTPException(status_code=404, detail='Account was not found')

        db_account.status = account.value

        await db.merge(db_account)
        await db.commit()
        return JSONResponse(content={"message": "Success update account"}, status_code=status.HTTP_200_OK)
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')

@router.get("/account/{id_account}/history", status_code=status.HTTP_200_OK)
async def get_account_history(id_account: int, db: DBD):
    """
    Returns the history of an account with the given id_account.

    Args:
    - id_account (int): The id of the account to retrieve the history for.
    - db (DBD): The database session dependency.

    Returns:
    - list[models.History]: A list of history objects associated with the account.

    Raises:
    - HTTPException(404): If the account with the given id_account is not found.
    """
    try:
        select_account = select(models.Account).where(models.Account.id == id_account)
        result = await db.execute(select_account)
        account = result.scalars().first()
        if not account:
            raise HTTPException(status_code=404, detail='Account was not found')

        select_history = select(models.History).where(models.History.id_account == id_account)
        result = await db.execute(select_history)
        history = result.scalars().all()

        return history
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')

@router.get("/account/{id_account}/tasks", status_code=status.HTTP_200_OK)
async def get_account_tasks(id_account: int, db: DBD):
    """
    Returns the tasks of an account with the given id_account.

    Args:
    - id_account (int): The id of the account to retrieve the tasks for.
    - db (DBD): The database session dependency.

    Returns:
    - list[models.Tasks]: A list of tasks objects associated with the account.

    Raises:
    - HTTPException(404): If the account with the given id_account is not found.
    """
    try:
        select_account = select(models.Account).where(models.Account.id == id_account)
        result = await db.execute(select_account)
        account = result.scalars().first()
        if not account:
            raise HTTPException(status_code=404, detail='Account was not found')

        select_tasks = select(models.Tasks).where(models.Tasks.id_group_sender == id_account)
        result = await db.execute(select_tasks)
        tasks = result.scalars().all()

        return tasks
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')

@router.get("/account/{id_account}/group_senders", status_code=status.HTTP_200_OK)
async def get_account_group_senders(id_account: int, db: DBD):
    """
    Retrieve all group senders associated with the given account ID.

    Args:
        id_account (int): The ID of the account to retrieve group senders for.
        db (DBD): The database dependency.

    Returns:
        List[models.Group_Senders]: A list of group senders associated with the given account ID.

    Raises:
        HTTPException: If the account with the given ID is not found.
    """
    try:
        select_account = select(models.Account).where(models.Account.id == id_account)
        result = await db.execute(select_account)
        account = result.scalars().first()
        if not account:
            raise HTTPException(status_code=404, detail='Account was not found')

        select_group_senders = select(models.Group_Senders).where(models.Group_Senders.id_account == id_account)
        result = await db.execute(select_group_senders)
        group_senders = result.scalars().all()

        return group_senders
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')

@router.get("/account/group_senders/{id_group_sender}", status_code=status.HTTP_200_OK)
async def get_account_by_group_sender(id_group_sender: int, db: DBD):
    """
    Retrieve an account by group sender ID.

    Args:
        id_group_sender (int): The ID of the group sender to retrieve the account for.
        db (DBD): The database dependency.

    Returns:
        models.Account: The account associated with the given group sender ID.

    Raises:
        HTTPException: If the group sender with the given ID is not found.
    """
    try:
        select_group_sender = select(models.Group_Senders).where(models.Group_Senders.id == id_group_sender)
        result = await db.execute(select_group_sender)
        group_sender = result.scalars().first()
        if not group_sender:
            raise HTTPException(status_code=404, detail='Group sender was not found')

        select_account = select(models.Account).where(models.Account.id == group_sender.id_account)
        result = await db.execute(select_account)
        account = result.scalars().first()
        if not account:
            raise HTTPException(status_code=404, detail='Account was not found')

        return account
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')

@router.delete("/account/{id_account}", status_code=status.HTTP_200_OK)
async def delete_account(id_account: int, db: DBD):
    """
    Delete an account from the database.

    Args:
        id_account (int): The ID of the account to delete.
        db (DBD): The database session.

    Returns:
        str: A success message.

    Raises:
        HTTPException: If the account with the specified ID is not found.
    """
    try:
        select_account = select(models.Account).where(models.Account.id == id_account)
        result = await db.execute(select_account)
        account = result.scalars().first()
        if not account:
            raise HTTPException(status_code=404, detail='Account was not found')
        await db.delete(account)
        await db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Success delete account"})
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Database integrity constraint violated')
