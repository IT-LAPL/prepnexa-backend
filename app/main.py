from fastapi import FastAPI

from .routers import users, uploads

app = FastAPI()

app.include_router(users.router)
app.include_router(uploads.router)


@app.get("/")
def root():
    return {"message": "FastAPI with uv is running 🚀"}
