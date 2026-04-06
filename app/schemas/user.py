# Schemas are spearate from models on purpose. Models represent DB tables, schemas represent what your API accepts and returns. 
# They are often similar but not the same


from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    """What we accept when someone registers."""
    username: str
    email: EmailStr  # EmailStr validates format - "notanemail" fails
    password: str # plaintext from client; we hash it in the router

class UserResponse(BaseModel):
    """What we send back - notice: no password field!"""
    id: int
    username: str
    email: str
    is_admin: bool
    created_at: datetime


    class Config:
        from_attributes = True
        # This tells Pydantic to read from ORM object attributes,
        # not just dict keys. Without this, UserResponse(orm_obj) fails.


class Token(BaseModel):
    access_token: str
    token_type: str # always "bearer" - part of OAuth spec

class TokenData(BaseModel):
    username: str | None = None