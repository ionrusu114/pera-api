""" Main """
from typing import Annotated
from fastapi import FastAPI, HTTPException,Depends,status
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from pera_fastapi import models
from .database import engine, SesssionLocal

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

class GroupBase(BaseModel):
    """ GroupBase baseModel"""
    name: str
    category: str = Field(default="MD")

def get_db():
    """ get DB function """
    db = SesssionLocal()
    try:
        yield db
    finally:
        db.close()

DBD = Annotated[Session, Depends(get_db)]

@app.post("/group/",status_code=status.HTTP_201_CREATED)
async def create_group(group: GroupBase, db: DBD):
    """ create_group endpoint"""
    db_group = models.Group(**group.dict())
    db.add(db_group)
    db.commit()

@app.get("/groups/",status_code=status.HTTP_200_OK)
async def get_all_groups(db: DBD):
    """ get_all_groups endpoint"""
    groups = db.query(models.Group).all()
    if groups is None:
        raise HTTPException(status_code=404,detail='Distributor was not found')
    return groups
