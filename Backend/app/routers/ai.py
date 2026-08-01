from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from ..database import get_db
from ..auth import get_current_user
from ..models import User, FarmerProfile, Plot, ActivityLog
from ai.engine import _generate
from ..crud import create_chat_message, get_chat_history
from ..schemas import AIChatMessageResponse

router = APIRouter(prefix="/api/ai", tags=["ai"])


class AIRequest(BaseModel):
    question: Optional[str] = None
    plot_id: Optional[str] = None


def get_month_name(date: datetime) -> str:
    months = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]
    return months[date.month - 1]


def build_farmer_context(current_user: User, plot_id: Optional[str], db: Session):
    profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == current_user.id).first()
    
    profile_text = "No profile details set up yet."
    if profile:
        profile_text = (
            f"Primary Crop: {profile.crop or 'Unknown'}, "
            f"Soil Type: {profile.soil_type or 'Unknown'}, "
            f"Irrigation: {profile.irrigation or 'Unknown'}, "
            f"Farming Experience: {profile.experience or 0} years."
        )

    # Validate and get plot context
    plot_text = "No plot selected or mapped."
    valid_plot_id = None

    if plot_id:
        plot = db.query(Plot).filter(Plot.id == plot_id, Plot.farmer_id == current_user.id).first()
        if plot:
            valid_plot_id = plot.id
            plot_text = (
                f"Plot Name: {plot.plot_name}, "
                f"Area: {plot.area_acres:.2f} acres ({plot.area_cents:.1f} cents), "
                f"Perimeter: {plot.perimeter_m:.1f} meters."
            )
            
    # Get last 15 activity logs
    logs = (
        db.query(ActivityLog)
        .filter(ActivityLog.farmer_id == current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(15)
        .all()
    )
    
    logs_text = "No activity logs recorded yet."
    if logs:
        logs_text = "\n".join(
            f"- {log.created_at.strftime('%Y-%m-%d')}: {log.entry_text} "
            f"(mode: {log.input_mode}, lang: {log.entry_language})"
            for log in logs
        )
        
    return profile_text, plot_text, logs_text, profile, valid_plot_id


@router.post("/ask")
def ask_ai(
    req: AIRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile_text, plot_text, logs_text, profile, valid_plot_id = build_farmer_context(current_user, req.plot_id, db)
    
    question = req.question or ""
    
    # Simple language detection based on Tamil character codes
    is_tamil = any("\u0b80" <= char <= "\u0bff" for char in question)
    if not question and profile and profile.language == "Tamil":
        is_tamil = True

    current_month = get_month_name(datetime.utcnow())

    if not question.strip():
        # Proactive advisory mode
        if is_tamil:
            system_instruction = (
                "நீ ஒரு விவசாய உதவியாளர். தமிழ் மொழியில் மட்டும் பதிலளிக்கவும். "
                "சீன எழுத்துக்கள் அல்லது பிற மொழிகளைப் பயன்படுத்தவேண்டாம்."
            )
            user_prompt = f"""விவசாயி சுயவிவரம்:
{profile_text}

நிலத்தின் விபரங்கள்:
{plot_text}

கடந்த 30 நாட்களின் குறிப்புகள்:
{logs_text}

நடப்பு மாதம்: {current_month}

இன்றைக்கு விவசாயி செய்ய வேண்டிய முக்கிய 2-3 பணிகளை சுருக்கமாக பட்டியலாக (bullet points) வழங்கவும்."""
        else:
            system_instruction = "You are an agricultural assistant for AgriTwin. Respond strictly in clear English."
            user_prompt = f"""Farmer Profile:
{profile_text}

Plot Details:
{plot_text}

Recent Logs:
{logs_text}

Current Month: {current_month}

Provide 2-3 concise, actionable task recommendations for today as bullet points."""
    else:
        # Question-Answering mode
        if is_tamil:
            system_instruction = (
                "நீ ஒரு விவசாய உதவியாளர். தமிழ் மொழியில் மட்டும் நேரடியாக பதிலளிக்கவும். "
                "சீன எழுத்துக்களையோ தேவையற்ற சொற்களையோ பயன்படுத்தவேண்டாம்."
            )
            user_prompt = f"""விவசாயி சுயவிவரம்:
{profile_text}

நிலத்தின் விபரங்கள்:
{plot_text}

கடந்த கால குறிப்புகள்:
{logs_text}

கேள்வி: "{question}" """
        else:
            system_instruction = "You are an agricultural assistant for AgriTwin. Output strictly in clear English."
            user_prompt = f"""Farmer Profile:
{profile_text}

Plot Details:
{plot_text}

Field History:
{logs_text}

User Question: "{question}" """

    # Save user question if present (using safe valid_plot_id to prevent foreign key errors)
    if question.strip():
        create_chat_message(db, current_user.id, valid_plot_id, "user", question)

    # Generate output using chat format
    response_text = _generate(prompt=user_prompt, system_prompt=system_instruction, max_new_tokens=300)

    # Save AI response safely
    create_chat_message(db, current_user.id, valid_plot_id, "ai", response_text)

    return {"response": response_text}


@router.post("/daily-brief")
def get_daily_brief(
    req: AIRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    req.question = ""
    return ask_ai(req, current_user, db)


@router.get("/chat-history", response_model=List[AIChatMessageResponse])
def get_history(
    plot_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_chat_history(db, current_user.id, plot_id)