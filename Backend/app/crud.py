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


def create_profile(db, user_id, profile):

    farmer = FarmerProfile(

        user_id=user_id,

        phone=profile.phone,

        state=profile.state,

        district=profile.district,

        village=profile.village,

        language=profile.language,

        farmer_type=profile.farmerType,

        experience=profile.experience,

        crop=profile.crop,

        irrigation=profile.irrigation,

        soil_type=profile.soilType,

    )

    db.add(farmer)
    db.commit()
    db.refresh(farmer)

    return farmer