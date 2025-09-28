from fastapi import FastAPI
from database import Base, engine
from routers import users, games

app = FastAPI()

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(games.router)
