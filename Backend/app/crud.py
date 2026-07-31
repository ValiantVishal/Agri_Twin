from sqlalchemy.orm import Session

from .models import User

from .auth import hash_password


def create_user(db: Session, name, email, password):

    user = User(

        name=name,

        email=email,

        password=hash_password(password)

    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user


def get_user_by_email(db, email):

    return db.query(User).filter(User.email == email).first()