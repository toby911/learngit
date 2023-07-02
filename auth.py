from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jose import jwt
from pydantic import BaseModel
from typing import List
import datetime

class UserModel(BaseModel):
    username: str
    password: str

class UserToken(BaseModel):
    code: int
    access_token: str
    token_type: str

# Replace the SECRET_KEY and ALGORITHM with your own values
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def login_for_access_token(usermodel: UserModel):
    user_name =  usermodel.username
    password = usermodel.password
    
    # Add logic to authenticate the user
    user_valid = False

    if user_valid:
        access_token_expires = datetime.timedelta(minutes=120)
        access_token = create_access_token(data={"sub": "admin"}, expires_delta=access_token_expires)
        return UserToken(code=0,access_token=access_token,token_type='Bearer')
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    return token

def create_access_token(*, data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
