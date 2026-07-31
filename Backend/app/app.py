from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from .database import Base
from .database import engine
from .database import get_db

from .models import User

from .schemas import Register
from .schemas import Login

from .crud import create_user
from .crud import get_user_by_email

from .auth import verify_password

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/register")

def register(user: Register, db: Session = Depends(get_db)):

    existing = get_user_by_email(db, user.email)

    if existing:

        raise HTTPException(400, "Email already exists")

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

        raise HTTPException(400, "Invalid Email")

    if not verify_password(user.password, db_user.password):

        raise HTTPException(400, "Wrong Password")

    return {

        "message": "Login Successful",

        "user": {

            "id": db_user.id,

            "name": db_user.name,

            "email": db_user.email

        }

    }