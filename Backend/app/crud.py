from sqlalchemy.orm import Session
from .models import User, FarmerProfile, Plot
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


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_profile(db: Session, user_id: int, profile):
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


# --- Plot CRUD operations ---

def get_plot(db: Session, plot_id: str):
    return db.query(Plot).filter(Plot.id == plot_id, Plot.is_active == True).first()


def get_plots_by_farmer(db: Session, farmer_id: int):
    return db.query(Plot).filter(Plot.farmer_id == farmer_id, Plot.is_active == True).all()


def create_plot(db: Session, plot_data: dict, farmer_id: int):
    plot = Plot(
        id=plot_data["id"],
        farmer_id=farmer_id,
        plot_name=plot_data["plot_name"],
        points=plot_data["points"],
        area_sqm=plot_data["area_sqm"],
        area_acres=plot_data["area_acres"],
        area_cents=plot_data["area_cents"],
        perimeter_m=plot_data["perimeter_m"]
    )
    db.add(plot)
    db.commit()
    db.refresh(plot)
    return plot


def update_plot(db: Session, db_plot: Plot, update_data: dict):
    for key, value in update_data.items():
        setattr(db_plot, key, value)
    db.commit()
    db.refresh(db_plot)
    return db_plot


def soft_delete_plot(db: Session, db_plot: Plot):
    db_plot.is_active = False
    db.commit()
    return db_plot