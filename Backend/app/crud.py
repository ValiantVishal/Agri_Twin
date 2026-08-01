from sqlalchemy.orm import Session
from .models import User, FarmerProfile, Plot, ActivityLog, AIChatMessage
from .auth import hash_password
from datetime import datetime
from typing import Optional


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


# --- ActivityLog CRUD operations ---

def create_activity_log(db: Session, farmer_id: int, activity_in) -> ActivityLog:
    plot_id = activity_in.plot_id
    if plot_id:
        exists = db.query(Plot).filter(Plot.id == plot_id).first()
        if not exists:
            plot_id = None

    db_activity = ActivityLog(
        farmer_id=farmer_id,
        plot_id=plot_id,
        entry_text=activity_in.entry_text,
        entry_language=activity_in.entry_language,
        input_mode=activity_in.input_mode,
        created_at=activity_in.created_at or datetime.utcnow()
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


def get_activity_logs(
    db: Session,
    farmer_id: int,
    plot_id: Optional[str] = None,
    date_start: Optional[datetime] = None,
    date_end: Optional[datetime] = None
):
    query = db.query(ActivityLog).filter(ActivityLog.farmer_id == farmer_id)
    if plot_id:
        query = query.filter(ActivityLog.plot_id == plot_id)
    if date_start:
        query = query.filter(ActivityLog.created_at >= date_start)
    if date_end:
        query = query.filter(ActivityLog.created_at <= date_end)
    return query.order_by(ActivityLog.created_at.desc()).all()


# --- AIChatMessage CRUD operations ---

def create_chat_message(db: Session, farmer_id: int, plot_id: Optional[str], sender: str, message_text: str) -> AIChatMessage:
    db_msg = AIChatMessage(
        farmer_id=farmer_id,
        plot_id=plot_id,
        sender=sender,
        message_text=message_text,
        created_at=datetime.utcnow()
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return db_msg


def get_chat_history(db: Session, farmer_id: int, plot_id: Optional[str] = None):
    query = db.query(AIChatMessage).filter(AIChatMessage.farmer_id == farmer_id)
    if plot_id:
        query = query.filter(AIChatMessage.plot_id == plot_id)
    return query.order_by(AIChatMessage.created_at.asc()).all()