from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import User, FarmerProfile
from .schemas import Register, Login, ProfileCreate
from .crud import create_user, get_user_by_email, create_profile
from .auth import verify_password, create_access_token, get_current_user
from .routers.plots import router as plots_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AgriTwin API")

import os

cors_origins_env = os.getenv("CORS_ORIGINS")
if cors_origins_env:
    origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
else:
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://agri-twin-omega.vercel.app",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register")
def register(user: Register, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Email"
        )
    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong Password"
        )

    # Generate JWT token
    access_token = create_access_token(data={"sub": db_user.email})

    return {
        "message": "Login Successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email
        }
    }


@app.post("/profile")
def save_profile(
    profile: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if profile already exists for user
    existing = db.query(FarmerProfile).filter(FarmerProfile.user_id == current_user.id).first()
    if existing:
        existing.phone = profile.phone
        existing.state = profile.state
        existing.district = profile.district
        existing.village = profile.village
        existing.language = profile.language
        existing.farmer_type = profile.farmerType
        existing.experience = profile.experience
        existing.crop = profile.crop
        existing.irrigation = profile.irrigation
        existing.soil_type = profile.soilType
        db.commit()
        db.refresh(existing)
        return {
            "message": "Profile updated",
            "profile_id": existing.id
        }

    farmer = create_profile(db, current_user.id, profile)
    return {
        "message": "Profile saved",
        "profile_id": farmer.id
    }


@app.get("/profile")
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return {
        "name": current_user.name,
        "email": current_user.email,
        "phone": profile.phone,
        "state": profile.state,
        "district": profile.district,
        "village": profile.village,
        "language": profile.language,
        "farmerType": profile.farmer_type,
        "experience": profile.experience,
        "crop": profile.crop,
        "irrigation": profile.irrigation,
        "soilType": profile.soil_type,
    }


# Include Plots Router
app.include_router(plots_router)