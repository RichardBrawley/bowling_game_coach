# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine, init_db
import models
from routers import users, games
from dotenv import load_dotenv
from rag_pipeline import document_store
from pdf_reader import load_pdf_to_documents
from rag_pipeline import indexing
import uuid


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

    # RAG: seed docs if first run, retrieve top K, generate feedback
    pdf_docs = load_pdf_to_documents("./pdf_files/Bowling.pdf")
    new_docs = []
    for d in pdf_docs:
        d.id = str(uuid.uuid4())   # assign a fresh unique ID
        new_docs.append(d)

    indexing.run({
        "embedder": {"documents": new_docs},
        "writer": {"policy": "skip"}
    })
    print("Documents indexed!")


app.include_router(users.router)
app.include_router(games.router)

@app.get("/")
def root():
    return {"ok2": True}

