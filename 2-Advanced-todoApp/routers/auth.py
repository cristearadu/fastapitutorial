import phonenumbers
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, EmailStr, validator
from models import Users
from database import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta
from jose import jwt, JWTError
from redis_config import redis_client

router = APIRouter(prefix="/auth", tags=["auth"])
SECRET_KEY = "3bb1d615bdfdf450ff38b425cb4d41d865331c9f3f9c7057b85dbfa2e08bb35f"
ALGORITHM = "HS256"
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="auth/token"
)  # need to verify token as a dependency in our requests


def validate_token(jti):
    if redis_client.exists(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is Blacklisted"
        )


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=2, description="Username")
    email: EmailStr = Field(description="Email Address")
    first_name: str = Field(min_length=2, description="First Name")
    last_name: str = Field(min_length=2, description="Last Name")
    password: str = Field(min_length=2, description="Password")
    role: str = Field(min_length=2, description="Role")
    phone_number: str = Field()

    @validator("email")
    def validate_email_domain(cls, value):
        allowed_domains = {"gmail.com", "yahoo.com", "outlook.com"}
        email_domain = value.split('@')[-1]
        if email_domain not in allowed_domains:
            raise ValueError("Invalid email domain!")
        return value

    @validator("role")
    def validate_role(cls, value):
        allowed_roles = {"admin", "casual_user"}
        if value not in allowed_roles:
            raise ValueError("Invalid role type!")
        return

    @validator("phone_number")
    def validate_phone_number(cls, value):
        try:
            number = phonenumbers.parse(value, "RO")
            if not phonenumbers.is_valid_number(number):
                raise ValueError("Phone number is not valid")
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number format")
        return value


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        # open up a DB connection only when it's requested
        # then close the connection
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    # security and verification
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        jti = payload.get("jti")
        validate_token(jti)

        user_id: int = payload.get("id")
        user_role: int = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return {"username": username, "id": user_id, "user_role": user_role}

    except JWTError:
        raise credentials_exception


def create_access_token(
    username: str, user_id: int, role: str, expires_delta: timedelta = None
):
    encode = {"sub": username, "id": user_id, "role": role}
    expires = (
        datetime.utcnow() + expires_delta
        if expires_delta
        else datetime.utcnow() + timedelta(minutes=15)
    )
    encode.update(
        {
            "exp": expires,
            "jti": str(uuid.uuid4()),  # Generate a unique JTI for each token
        }
    )

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def check_user_with_same_username_exists(db: db_dependency, username):
    existing_username = db.query(Users).filter(Users.username == username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username Already Registered"
        )


def check_user_with_same_emaiL_address_exists(db: db_dependency, email_address):
    existing_username = db.query(Users).filter(Users.email == email_address).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email Address Already Registered"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):

    check_user_with_same_username_exists(db, create_user_request.username)
    check_user_with_same_emaiL_address_exists(db, create_user_request.email)

    # make sure the user is equal to our model
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True,
        phone_number=create_user_request.phone_number
    )

    db.add(create_user_model)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=20)
    )
    return {"access_token": token, "token_type": "Bearer"}
