# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine, init_db
import models
from routers import users, games
from dotenv import load_dotenv
from rag_pipeline import document_store

load_dotenv()

app = FastAPI(title="Bowling LLM Backend (PGVector RAG)")

# Allow frontend (React) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()                   # ensures CREATE EXTENSION vector
    Base.metadata.create_all(bind=engine)  # users, games, documents tables
    try:
        document_store.write_documents([])
    except Exception as e:
        print(f"Document store init error: {e}")


app.include_router(users.router)
app.include_router(games.router)

@app.get("/")
def root():
    return {"ok2": True}

