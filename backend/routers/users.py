from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    new_user = User(username=username, password_hash=hash_password(password))
    db.add(new_user)
    db.commit()
    return {"ok": True, "msg": "User registered"}

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return {"ok": True, "access_token": token, "token_type": "bearer"}

@router.get('/test')
def test():
    return {'code': "OK"}