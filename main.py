# standard extras in python pip install "fastapi[standard]" to leverage the extra requirements
from fastapi import FastAPI

app = FastAPI()

@app.get("/ ")
def home():
    return {"message": "Hello World!"}