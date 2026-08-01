from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from ..database import get_db
from ..auth import get_current_user
from ..models import User, FarmerProfile, Plot, ActivityLog
from Backend.engine import _generate  # FIXED: Adjusted import path to match backend structure
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
            f"Farmer Name: {current_user.name or 'Unknown'}, "
            f"Preferred Language: {profile.language or 'Tamil'}, "
            f"Primary Crop: {profile.crop or 'Unknown'}, "
            f"Soil Type: {profile.soil_type or 'Unknown'}, "
            f"Irrigation: {profile.irrigation or 'Unknown'}, "
            f"Farming Experience: {profile.experience or 0} years."
        )

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

    question = (req.question or "").strip()

    is_tamil = any("\u0b80" <= char <= "\u0bff" for char in question)
    if not question and profile and profile.language == "Tamil":
        is_tamil = True

    current_month = get_month_name(datetime.utcnow())

    # Case 1: Daily Brief / Recommendation (No direct question provided)
    if not question:
        if is_tamil:
            system_instruction = (
                "நீ ஒரு தமிழக கிராமப்புற விவசாய உதவியாளர். விவசாயிகளின் கேள்விகளுக்கு எளிய முறையில், துல்லியமான தமிழ் மொழியில் பதில் அளிக்கவும்."
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

        response_text = _generate(prompt=user_prompt, system_prompt=system_instruction, max_new_tokens=300)
        create_chat_message(db, current_user.id, valid_plot_id, "ai", response_text)
        return {"response": response_text}

    # Save user message to database
    create_chat_message(db, current_user.id, valid_plot_id, "user", question)

    # Case 2: Memory Lookup (Querying farmer profile/logs)
    if is_tamil:
        memory_system_instruction = (
            "நீ ஒரு தமிழக கிராமப்புற விவசாய உதவியாளர். வழங்கப்பட்டுள்ள விவசாய குறிப்புகளின் அடிப்படையில் மட்டுமே கேள்விக்கு நேரடியாக தமிழில் பதிலளிக்கவும்."
        )
        memory_user_prompt = f"""விவசாய குறிப்புகள்:
{profile_text}

கடந்த கால குறிப்புகள்:
{logs_text}

கேள்வி: "{question}" """
    else:
        memory_system_instruction = (
            "You are an agricultural assistant for AgriTwin. "
            "Answer the user's question strictly using the provided farmer profile and past activity logs. "
            "If the answer is not contained within these logs, respond with exactly: "
            "'This information is not available in your records.' Do not provide any general advice or external facts."
        )
        memory_user_prompt = f"""Farmer Profile:
{profile_text}

Field History / Logs:
{logs_text}

User Question: "{question}" """

    memory_response = _generate(prompt=memory_user_prompt, system_prompt=memory_system_instruction, max_new_tokens=150)

    # Check if memory search had an answer
    not_found_indicators_en = ["information is not available", "not available in your records", "not found", "does not contain"]
    not_found_indicators_ta = ["விபரம் குறிப்பிடப்படவில்லை", "தகவல் இல்லை", "குறிப்பிடப்படவில்லை"]

    is_not_found = (
        any(ind in memory_response.lower() for ind in not_found_indicators_en) or
        any(ind in memory_response for ind in not_found_indicators_ta)
    )

    if not is_not_found:
        response_text = memory_response
    else:
        # Case 3: Fallback to General Agricultural Knowledge Base
        if is_tamil:
            general_system_instruction = (
                "நீ ஒரு தமிழக கிராமப்புற விவசாய உதவியாளர். விவசாயிகளின் கேள்விகளுக்கு எளிய முறையில், துல்லியமான தமிழ் மொழியில் பதில் அளிக்கவும்."
            )
            general_user_prompt = f"""விவசாயி சுயவிவரம்:
{profile_text}

நிலத்தின் விபரங்கள்:
{plot_text}

கேள்வி: "{question}" """
        else:
            general_system_instruction = "You are an agricultural assistant for AgriTwin. Output strictly in clear English."
            general_user_prompt = f"""Farmer Profile:
{profile_text}

Plot Details:
{plot_text}

User Question: "{question}" """

        response_text = _generate(prompt=general_user_prompt, system_prompt=general_system_instruction, max_new_tokens=300)

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