from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from database import SessionLocal
from models import Game, User
from rag_pipeline import rag_pipeline
from auth import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/games", tags=["games"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).get(int(user_id))
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/summarize")
def summarize(scores: list[int], token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    total_score = sum(scores)

    game = Game(user_id=user.id, scores=scores, total=total_score)
    db.add(game)
    db.commit()
    db.refresh(game)

    question = f"Player {user.username} scored {total_score} with frame scores {scores}. Give coaching feedback."
    result = rag_pipeline.run(query=question, params={"Retriever": {"top_k": 3}})

    feedback = result["answers"][0].answer if result["answers"] else "No feedback."
    return {"total_score": total_score, "feedback": feedback}
