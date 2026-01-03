from fastapi import FastAPI

from .routers import users, uploads, papers

app = FastAPI()

app.include_router(users.router)
app.include_router(uploads.router)
app.include_router(papers.router)


@app.get("/")
def root():
    return {"message": "FastAPI with uv is running 🚀"}
