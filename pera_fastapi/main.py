""" Main """
from typing import Annotated
from fastapi import FastAPI, HTTPException,Depends,status
from .schemas import GroupBase
from sqlalchemy.orm import Session
from pera_fastapi import models
from .database import engine, SesssionLocal,get_db

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

DBD = Annotated[Session, Depends(get_db)]

@app.post("/group/",status_code=status.HTTP_201_CREATED)
async def create_group(group: GroupBase, db: DBD):
    """ create_group endpoint"""
    db_group = models.Group(**group.dict())
    db.add(db_group)
    db.commit()
    return "Success add group"

@app.get("/groups/",status_code=status.HTTP_200_OK)
async def get_all_groups(db: DBD):
    """ get_all_groups endpoint"""
    groups = db.query(models.Group).all()
    if groups is None:
        raise HTTPException(status_code=404,detail='Groups was not found')
    return groups

@app.get("/group/{id_group}",status_code=status.HTTP_200_OK)
async def get_group(id_group: int, db: DBD):
    """ get_group endpoint"""
    group = db.query(models.Group).filter(models.Group.id == id_group).first()
    if group is None:
        raise HTTPException(status_code=404,detail='Group was not found')
    return group


@app.delete("/group/{id_group}",status_code=status.HTTP_200_OK)
async def delete_group(id_group: int, db: DBD):
    db_group = db.query(models.Group).filter(models.Group.id == id_group).first()
    if db_group is None:
        raise HTTPException(status_code=404,detail='Group was not found')
    db.delete(db_group)
    db.commit()
    return "Success delete group - {}".format(id_group)
        
