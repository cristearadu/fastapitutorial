from models import Todos
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, Request
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/todo",
                   tags=["todo"],
                   responses={404: {"description": "Not found"}})

templates = Jinja2Templates(directory="templates")


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


class TodoRequest(BaseModel):
    # not want to pass the ID because it's autoincremented and unique to the DB
    title: str = Field(min_length=3)
    description: str = Field(min_length=3)
    priority: int = Field(gt=0, lt=6)
    complete: bool = Field(bool)


@router.get("/test")
async def test(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    # the app doesn't know how many ids there are within the app, even if it's a primary key
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found.")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_todo(
    user: user_dependency, db: db_dependency, todo_request: TodoRequest
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo_model = Todos(**todo_request.dict(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    todo_request: TodoRequest,  # needs to be above every PATH PARAMETER
    todo_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")

    # need to use the same to do model that we retrieve above
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")

    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
