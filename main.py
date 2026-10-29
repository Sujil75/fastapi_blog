# standard extras in python pip install "fastapi[standard]" to leverage the extra requirements
# Request is required to run Jinja2
# HTTPException, status are used to raise an error when invalid data is send into the path parameter
from pathlib import Path
from typing import Annotated

from fastapi import (  #  Depends is for dependency injection, it injects db session into routes
    Depends,
    FastAPI,
    HTTPException,
    Request,
    status,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select  # select is for querying
from sqlalchemy.orm import Session  # session is for type hints
from starlette.exceptions import (
    HTTPException as StarletteHTTPException,  # fastapi is built on top of starlette, fastapi only covers the normal errors but not "Page not found" error or something so for that starlette is required since, starlette provides those errors.
)

import models

# Base and engine are for tables; get_db is dependency function to provide db session
from database import Base, engine, get_db
from schemas import PostCreate, PostResponse, UserCreate, UserResponse

# Right after the imports of models and database
Base.metadata.create_all(
    bind=engine
)  # this is idempotent means can be run multiple times safely; runs at app startup

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")
templates = Jinja2Templates(directory="templates")


profile_pic = Path("static/profile_pics")


# @app.get("/", response_class=HTMLResponse, include_in_schema=False) # Will not show HTML tag related data in documentation
# @app.get("/posts", response_class=HTMLResponse) # Will show HTML tag related data in documentation, since not using include_in_schema(default is true, if not implemented)
# Home Page
@app.get(
    "/", include_in_schema=False, name="home"
)  # url will take home as router, if not given explicitly then posts is taken since its a named router
@app.get(
    "/posts", include_in_schema=False, name="posts"
)  # url will take posts as route name
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    # return f"<h1>{posts[0]['title']}</h1>"
    # return templates.TemplateResponse(
    #     request, "home.html", {"posts": posts, "title": "Home"}
    # )

    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "posts": posts,
            "title": "Home",
        },
    )


# Post page
@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(
    request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]
):  # post_id should be given with data type, so if any invalid data type is given then FastAPI automatically raises an error
    # for post in posts:
    #     if post_id == post.get("id"):
    #         # return post # this will given json

    #         title = post["title"][:50]  # Title chars upto only 50 will be shown
    #         return templates.TemplateResponse(
    #             request, "post.html", {"post": post, "title": title}
    #         )

    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()

    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request,
            "post.html",
            {
                "post": post,
                "title": title,
            },
        )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

# Get user posts HTML
@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {
            "posts": posts,
            "user": user,
            "title": f"{user.username}'s Posts"
        }
    )


# Create user
@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user: UserCreate, db: Annotated[Session, Depends(get_db)]
):  # passes get_db as a result to db
    # To check already existing user
    result = db.execute(
        select(models.User).where(
            models.User.username == user.username
        )  # this is a db query
    )
    existing_user = (
        result.scalars().first()
    )  # this will give the first same user detail

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    # To check already existing email
    result = db.execute(select(models.User).where(models.User.email == user.email))
    existing_email = (
        result.scalars().first()
    )  # this will give the first same user detail

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already taken",
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# Get user
@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))

    user = result.scalars().first()

    if user:
        return user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )


# Get user posts
@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return posts


@app.get(
    "/api/posts", response_model=list[PostResponse]
)  # fastapi matches that all the posts match the PostResponse schema and doc will show the exact structure
def get_posts():
    return posts


## Create Post
@app.post(
    "/api/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(post: PostCreate):
    new_id = max(p["id"] for p in posts) + 1 if posts else 1
    new_post = {
        "id": new_id,
        "author": post.author,
        "title": post.title,
        "content": post.content,
        "date_posted": "April 23, 2025",
    }

    posts.append(new_post)
    return new_post


@app.get("/api/posts/{post_id}", response_model=PostResponse)  # for a single post
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please, check your response and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,  # here, exceptions won't have any error status but will be 422 status code error
            content={"detail": exception.errors()},
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please, check your input and try again",  # exception.errors() will show all the technical details to normal users which here isn't required
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
