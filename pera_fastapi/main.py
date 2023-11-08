
from fastapi import FastAPI, HTTPException,Depends,status
from pydantic import BaseModel,EmailStr,Field
from enum import Enum
from typing import Annotated
import pera_fastapi.models as models
from .database import engine, SesssionLocal
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import json
from fastapi.security import OAuth2PasswordBearer

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class GroupBase(BaseModel):
    name: str
    category: str = Field(default="MD")

def get_db():
    db = SesssionLocal()

    try:
        yield db
    finally:
        db.close()
    
db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/group/",status_code=status.HTTP_201_CREATED)
async def create_group(group: GroupBase, db: db_dependency):
    db_group = models.Group(**group.dict())
    db.add(db_group)
    db.commit()

@app.get("/groups/",status_code=status.HTTP_200_OK)
async def get_all_groups(db: db_dependency):
    groups = db.query(models.Group).all() 
    if groups is None:
        HTTPException(status_code=404,detail='Distributor was not found')
    return groups











