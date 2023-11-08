
from fastapi import FastAPI, HTTPException,Depends,status
from pydantic import BaseModel,EmailStr,Field
from enum import Enum
from typing import Annotated
import models
from pera_fastapi.models import models
from database import engine, SesssionLocal
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











