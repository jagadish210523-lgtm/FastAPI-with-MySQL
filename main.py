from fastapi import FastAPI, HTTPException,Depends,status
from pydantic import BaseModel
from typing import Annotated
from . import models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session

jaga = FastAPI()
models.Base.metadata.create_all(bind = engine)


class PostBase(BaseModel):
    title : str
    content : str
    user_id : int

class UserBase(BaseModel):
    username : str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@jaga.get("/posts/{post_id}",status_code = status.HTTP_200_OK)
async def get_required_post(post_id : int, db : db_dependency):
    posts = db.query(models.Post).filter(models.Post.id == post_id).first()
    if posts is None:
        raise HTTPException(status_code = 404, detail = "Post not found")
    return posts


@jaga.get("/posts",status_code = status.HTTP_200_OK)
async def get_posts(db: db_dependency):
    posts = db.query(models.Post).all()
    return posts


@jaga.post("/posts",status_code = status.HTTP_201_CREATED)
async def new_post(id : PostBase, db : db_dependency):
    new_post = models.Post(**id.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@jaga.delete("/posts/{post_id}",status_code = status.HTTP_200_OK)
async def delete_post(post_id : int, db : db_dependency):
    remove_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if remove_post is None:
        raise HTTPException(status_code = 404, detail = "Post not found")
    db.delete(remove_post)
    db.commit()


@jaga.put("/posts/{post_id}", status_code = status.HTTP_200_OK)
async def change_post(post_id : int, post : PostBase, db : db_dependency):
    update_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if update_post is None:
        raise HTTPException(status_code = 404, detail = "Post not found")
    update_post.title = post.title
    update_post.content = post.content
    update_post.user_id = post.user_id
    db.commit()
    return update_post