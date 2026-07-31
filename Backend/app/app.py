from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# Database and Models
from app.database import Base, engine, get_db
from app.models import User
from app.schemas import Register, Login
from app.crud import create_user, get_user_by_email
from app.auth import verify_password

# Voice Router
from app.router.voice import router as voice_router

# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AgriTwin API")

# Include the Voice Router
app.include_router(voice_router)


# --- AUTHENTICATION ROUTES ---

@app.post("/register")
def register(user: Register, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = create_user(
        db,
        user.name,
        user.email,
        user.password
    )
    return {
        "message": "User Registered Successfully",
        "id": new_user.id
    }


@app.post("/login")
def login(user: Login, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid Email")
    
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Wrong Password")
    
    return {
        "message": "Login Successful",
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email
        }
    }


@app.get("/")
def root():
    return {"message": "AgriTwin Backend is running!"}