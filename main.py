from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import blog_routes, user_routes

app = FastAPI()

app.include_router(blog_routes.router)
app.include_router(user_routes.router)

app.mount("/", StaticFiles(directory="client_build", html=True), name="frontend")
