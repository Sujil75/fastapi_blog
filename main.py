# standard extras in python pip install "fastapi[standard]" to leverage the extra requirements
# Request is required to run Jinja2
# HTTPException, status are used to raise an error when invalid data is send into the path parameter
from fastapi import FastAPI, Request, HTTPException, status
# from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
profile_pic = Path("static/profile_pics")

posts: list[dict] = [
    {
        "id": 1,
        "author": {
            "username": "Corey Schafer",
            "image_path": profile_pic / "default.jpg",
        },
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    }, {
        "id": 2,
        "author": {
            "username": "Jane Doe",
            "image_path": profile_pic / "default.jpg",
        },
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better",
        "date_posted": "April 21, 2025",
    }
]

# @app.get("/", response_class=HTMLResponse, include_in_schema=False) # Will not show HTML tag related data in documentation
# @app.get("/posts", response_class=HTMLResponse) # Will show HTML tag related data in documentation, since not using include_in_schema(default is true, if not implemented)
@app.get("/", include_in_schema=False, name="home") # url will take home as router, if not given explicitly then posts is taken since its a named router
@app.get("/posts", include_in_schema=False, name="posts") # url will take posts as route name
def home(request: Request):
    # return f"<h1>{posts[0]['title']}</h1>"
    return templates.TemplateResponse(
        request, 
        "home.html", 
        {"posts": posts, "title": "Home"}
    )

@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int): # post_id should be given with data type, so if any invalid data type is given then FastAPI automatically raises an error
    for post in posts:
        if post_id == post.get("id"):
            # return post # this will given json
            
            title = post['title'][:50] # Title chars upto only 50 will be shown
            return templates.TemplateResponse(
                request, 
                "post.html", 
                {"post": post, "title": title}
            )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.get("/api/posts")
def get_posts():
    return posts

@app.get("/api/posts/{post_id}")
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")