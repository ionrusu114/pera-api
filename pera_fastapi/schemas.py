from pydantic import BaseModel,Field

class GroupBase(BaseModel):
    """ GroupBase baseModel"""
    name: str
    category: str = Field(default="MD")

