# standard extras in python pip install "fastapi[standard]" to leverage the extra requirements
# Request is required to run Jinja2
from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    }, {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better",
        "date_posted": "April 21, 2025",
    }
]

# @app.get("/", response_class=HTMLResponse, include_in_schema=False) # Will not show HTML tag related data in documentation
# @app.get("/posts", response_class=HTMLResponse) # Will show HTML tag related data in documentation, since not using include_in_schema(default is true, if not implemented)
@app.get("/", include_in_schema=False)
@app.get("/posts", include_in_schema=False)
def home(request: Request):
    # return f"<h1>{posts[0]['title']}</h1>"
    return templates.TemplateResponse(request, "home.html", {"posts": posts, "title": "Home"})

@app.get("/api/posts")
def get_posts():
    return posts