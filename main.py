from fastapi import FastAPI,Depends
import uvicorn
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Post,User,like,dislike
from fastapi_users import fastapi_users, FastAPIUsers
from auth.auth import auth_backend
from auth.database import User
from auth.manager import get_user_manager
from auth.schemas import UserRead, UserCreate
from datetime import datetime

engine = create_engine("sqlite:///db.sqlite3")
session = sessionmaker(bind=engine)
s = session()

description = """
Тестовое задание для собеседования в Webtronics. 🚀
"""
tags_metadata = [
    {
        "name": "auth",
        "description": "**Регистрация**, **авторизация**, и **выход из аккаунта** тут. !Для авторизации в параметр username указывайте почту!!",
    },
    {
        "name": "watch and add posts",
        "description": "**Список** и **создание** постов тут. Доступно только авторизованым пользователям.",
    },
    {
        "name": "watch, upadte and delete post",
        "description": "**Подробная информация**, **редакиторвание** и **удаление** постов тут. Доступно только авторизованым пользователям.",
    },
    {
        "name": "Like and dislike",
        "description": "**Лайки** и **дизлайки** постов тут. Доступно только авторизованым пользователям.",
    },
]

app = FastAPI(title='Social networking application API',description=description,openapi_tags=tags_metadata)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

current_user = fastapi_users.current_user()

@app.get("/posts", tags=["watch and add posts"])
async def posts(user: User = Depends(current_user)):
    posts = []
    for i in s.query(Post).all():
        post = {'id':i.id,
        'text':i.text,
        'userfrom':i.userfrom}
        posts.append(post)
    return posts

@app.post("/posts", tags=["watch and add posts"])
async def posts(text: str ,user: User = Depends(current_user)):
    s.add(Post(userfrom=user.id, text=text))
    s.commit()
    return {'result': 'post added!'}

@app.get("/post/{id}", tags=["watch, upadte and delete post"])
async def post(id: int ,user: User = Depends(current_user)):
    post = s.query(Post).get(id)
    post.likes = s.query(like).filter(like.post == id).count()
    post.dislikes = s.query(dislike).filter(dislike.post == id).count()
    return post

@app.put("/post/{id}", tags=["watch, upadte and delete post"])
async def post(id: int,text: str ,user: User = Depends(current_user)):
    if s.get(Post, id).userfrom == user.id:
        s.query(Post).filter(Post.id == id).update({'text':text})
        s.query(Post).filter(Post.id == id).update({'updated_on': datetime.now()})
        s.commit()
        return {'result': 'post updated!'}
    else:
        return {'result': 'you cant update not your post!'}


@app.delete("/post/{id}", tags=["watch, upadte and delete post"])
async def delete(id: int ,user: User = Depends(current_user)):
    try:
        if s.get(Post,id).userfrom == user.id:
            s.query(Post).filter(Post.id == id).delete()
            s.query(like).filter(like.post == id).delete()
            s.query(dislike).filter(dislike.post == id).delete()
            s.commit()
            return {'result': 'post deleted!'}
        else:
            return {'result': 'you cant delete not your post!'}
    except:
        return {'result': 'post not found!'}

@app.get("/post/like/{id}", tags=["Like and dislike"])
async def likee(id: int,user: User = Depends(current_user)):
    userid = user.id
    postid = id
    if s.query(Post).get(postid).userfrom == userid:
        return {'result': 'you cant like your post!'}
    else:
        if s.query(dislike).filter(dislike.post == postid, dislike.user == userid).count() == 1:
            s.query(dislike).filter(dislike.post == postid, dislike.user == userid).delete()
        if s.query(like).filter(like.post == postid, like.user == userid).count() == 1:
            s.query(like).filter(like.post == postid, like.user == userid).delete()
            s.commit()
            return {'result': 'unliked!'}
        s.add(like(post=postid, user=userid))
        s.commit()
        return {'result': 'liked!'}

@app.get("/post/dislike/{id}", tags=["Like and dislike"])
async def dislikee(id: int ,user: User = Depends(current_user)):
    userid = user.id
    postid = id
    if s.query(Post).get(postid).userfrom == userid:
        return {'result': 'you cant dislike your post!'}
    else:
        if s.query(like).filter(like.post==postid,like.user==userid).count()==1:
            s.query(like).filter(like.post==postid,like.user==userid).delete()
        if s.query(dislike).filter(dislike.post==postid,dislike.user==userid).count()==1:
            s.query(dislike).filter(dislike.post == postid, dislike.user == userid).delete()
            s.commit()
            return {'result': 'undisliked!'}
        s.add(dislike(post = postid,user = userid))
        s.commit()
        return {'result':'disliked!'}



if __name__=='__main__':
    uvicorn.run(app, host="localhost", port=5000, log_level="info")