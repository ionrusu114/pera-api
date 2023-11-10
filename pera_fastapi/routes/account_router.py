from typing import Annotated
from fastapi import APIRouter, HTTPException,Depends,status
from pera_fastapi.models.schemas import AccountBase,StatusAccount
from sqlalchemy.orm import Session
from pera_fastapi.models import models
from pera_fastapi.models.database import engine, get_db,SesssionLocal


DBD = Annotated[Session, Depends(get_db)]

router = APIRouter()

@router.post("/account/",status_code=status.HTTP_201_CREATED)
async def create_account(account: AccountBase, db: DBD):
    """
    Create a new account in the database.

    Args:
        account (models.Account): The account data to be added.
        db (DBD): The database session.

    Returns:
        str: A success message.
    """
    db_account = models.Account(**account.dict())
    db.add(db_account)
    db.commit()
    return "Success add account"

@router.get("/accounts/",status_code=status.HTTP_200_OK)
async def get_all_accounts(db: DBD):
    """
    Retrieve all accounts.

    Returns:
        List[models.Account]: A list of all accounts.
    
    Raises:
        HTTPException: If no accounts are found.
    """
    accounts = db.query(models.Account).all()
    if accounts is None:
        raise HTTPException(status_code=404,detail='Accounts was not found')
    return accounts

@router.get("account/{id_account}",status_code=status.HTTP_200_OK)
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
    account = db.query(models.Account).filter(models.Account.id == id_account).first()
    if account is None:
        raise HTTPException(status_code=404,detail='Account was not found')
    return account

@router.put("/account/{id_account}",status_code=status.HTTP_200_OK)
async def update_account(id_account: int, account: StatusAccount, db: DBD):
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
    db_account = db.query(models.Account).filter(models.Account.id == id_account).first()
    if db_account is None:
        raise HTTPException(status_code=404,detail='Account was not found')
    db_account.status = account.status
    db.commit()
    return { "message": "Success update account","status":status.HTTP_200_OK}

@router.delete("/account/{id_account}",status_code=status.HTTP_200_OK)
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
    db_account = db.query(models.Account).filter(models.Account.id == id_account).first()
    if db_account is None:
        raise HTTPException(status_code=404,detail='Account was not found')
    db.delete(db_account)
    db.commit()
    return { "message": "Success delete account","status":status.HTTP_200_OK}

