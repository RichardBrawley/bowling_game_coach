# backend/routers/games.py
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from database import SessionLocal
from models import Game, User
from auth import SECRET_KEY, ALGORITHM
import rag_pipeline
from pydantic import BaseModel
from haystack.dataclasses import Document
from rag_pipeline import indexing
from time import time

router = APIRouter()

class SummarizeRequest(BaseModel):
    scores: list[int]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).get(uid)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/summarize")
def summarize(payload: SummarizeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    scores = payload.scores
    if not scores:
        raise HTTPException(status_code=400, detail="Scores missing")

    total = sum(scores)
    game = Game(user_id=user.id, scores=scores, total=total)
    db.add(game)
    db.commit()

    # RAG: seed docs if first run, retrieve top K, generate feedback
    docs = [
        Document(id=f"game1:{user.id}:{int(time())}", content="A strike means knocking down all 10 pins with the first ball."),
        Document(id=f"game2:{user.id}:{int(time())}", content="Spare shooting is crucial — always aim at the key pin."),
        Document(id=f"game3:{user.id}:{int(time())}", content="Consistent release and targeting arrows improve accuracy."),
    ]
    indexing.run({
        "embedder": {"documents": docs},
        "writer": {"policy": "skip"}
    })
    print("Documents indexed!")

    question = f"Analyze my bowling game (total {total}, per-frame {scores}). Give tips to improve next game."

    result = rag_pipeline.rag_pipeline.run(
        {
            "query_embedder": {"text": question},
            "prompt_builder": {"query": question}
        }
    )
    feedback = result["generator"]["replies"][0]

    return {"total_score": total, "feedback": feedback}
