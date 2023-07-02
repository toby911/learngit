from fastapi.security import OAuth2PasswordBearer
from fastapi import Request, HTTPException,Depends
from pydantic import BaseSettings
# from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt , JWTError
from db.db_users import Users
from typing import Optional, Union

class UserTokenConfig(BaseSettings):
    """对用户登录时处理token的相关配置"""
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # 通过命令行 `openssl rand -hex 32` 可以生成该安全密钥
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

user_token_conf = UserTokenConfig()

__oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login/token")
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_pwd_hash(pwd):
    return pwd_context.hash(pwd)

# def authenticate_user( username: str, password: str) -> Union[bool, Users]:
#     """
#     验证用户合法性
#     :return: 若验证成功则返回 User 对象；若验证失败则返回 False
#     """
#     # if not pwd_context.verify(password, user.hashed_password):
#         # return False
#     return True

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, user_token_conf.SECRET_KEY, algorithm=user_token_conf.ALGORITHM)
    return encoded_jwt


async def fetch_token(request: Request) -> Optional[str]:
    """
    在 request 中获取到 oauth2 认证所需要的信息
    :return: 取出的 token
    """
    try:
        token = await __oauth2_scheme(request)
    except HTTPException as e:
        raise JWTError(e.detail)
    return token


def verify_token(token: str = Depends(fetch_token)) -> str:
    """
    根据请求头部的 Authorization 字段，在 Redis 进行验证并获取用户的 username
    :return: 验证成功时返回用户的 username，验证失败则抛出异常
    :raise: TokenVerifyException 验证失败时抛出此异常
    """
    # 验证 token 是否为空
    if token is None:
        raise JWTError()
    # 查询 redis_db 进行验证
    payload = jwt.decode(token, key=user_token_conf.SECRET_KEY, algorithms=user_token_conf.ALGORITHM) 
    username: str = payload["username"]

    if username is None:
        raise JWTError()
    return username


# 模拟用户认证
def authenticate_user(token: str):
    try:
        payload = jwt.decode(token, user_token_conf.SECRET_KEY, algorithms=user_token_conf.ALGORITHM)
        # 在这里可以根据payload中的信息进行用户认证和授权逻辑
        # 这里简单地返回用户ID
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")