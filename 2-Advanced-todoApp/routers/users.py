from models import Users
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from .auth import get_current_user, oauth2_bearer, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from redis_config import redis_client


router = APIRouter(prefix="/user", tags=["user"])

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def blacklist_token(jti):
    redis_client.set(name=jti, value="true", ex=3600)


def get_tokens_jti(user_id: int) -> str:
    jti_key = f"user_tokens:{user_id}"
    jti = redis_client.get(jti_key)
    return jti


def get_db():
    db = SessionLocal()
    try:
        # open up a DB connection only when it's requested
        # then close the connection
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class UserVerification(BaseModel):
    initial_password: str
    password_to_change: str = Field(min_length=6)


class DeleteUser(BaseModel):
    password: str


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    return user_model


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user: user_dependency, db: db_dependency, user_verification: UserVerification
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if not bcrypt_context.verify(
        user_verification.initial_password, user_model.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Passwords do not match!")

    user_model.hashed_password = bcrypt_context.hash(
        user_verification.password_to_change
    )
    db.commit()


@router.put("/phone_number/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user: user_dependency,
    db: db_dependency,
    password: DeleteUser,
    token: Annotated[str, Depends(oauth2_bearer)],
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if not bcrypt_context.verify(password.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Passwords do not match!")

    jti = payload.get("jti")

    if jti:
        blacklist_token(jti)

    db.query(Users).filter(Users.id == user.get("id")).delete()
    db.commit()
