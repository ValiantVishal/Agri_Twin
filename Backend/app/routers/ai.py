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

    # Get plot context
    plot_text = "No plot selected or mapped."
    if plot_id:
        plot = db.query(Plot).filter(Plot.id == plot_id, Plot.farmer_id == current_user.id).first()
        if plot:
            plot_text = (
                f"Plot Name: {plot.plot_name}, "
                f"Area: {plot.area_acres:.2f} acres ({plot.area_cents:.1f} cents), "
                f"Perimeter: {plot.perimeter_m:.1f} meters."
            )
            
    # Get last 15 activity logs for memory bank context
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
        
    return profile_text, plot_text, logs_text, profile


@router.post("/ask")
def ask_ai(
    req: AIRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile_text, plot_text, logs_text, profile = build_farmer_context(current_user, req.plot_id, db)
    
    question = req.question or ""
    
    # Simple language detection based on Tamil characters
    is_tamil = any("\u0b80" <= char <= "\u0bff" for char in question)
    if not question and profile and profile.language == "Tamil":
        is_tamil = True

    current_month = get_month_name(datetime.utcnow())

    if not question.strip():
        # Proactive advisory mode
        if is_tamil:
            prompt = f"""நீ ஒரு விவசாய உதவியாளர். விவசாயியின் பின்வரும் சுயவிவரம் மற்றும் கடந்த கால குறிப்புகளின் அடிப்படையில் இன்றைக்கு செய்ய வேண்டிய பணிகளை சுருக்கமாக பட்டியலிடு.
            
விவசாயி சுயவிவரம்:
{profile_text}

நிலத்தின் விபரங்கள்:
{plot_text}

கடந்த 30 நாட்களின் குறிப்புகள்:
{logs_text}

நடப்பு மாதம்: {current_month}

விதிமுறைகள்:
1. தமிழ் மொழியில் மட்டும் பதிலளிக்கவும்.
2. சீன மொழியிலோ அல்லது வேறு மொழிகளிலோ எழுதக்கூடாது. தமிழ் மற்றும் ஆங்கில வார்த்தைகளைத் தவிர வேறு எழுத்துக்களைப் பயன்படுத்தவேண்டாம்.
3. சுருக்கமாகவும், எளிமையாகவும், விவசாயி உடனடியாக செய்யக்கூடிய அறிவுரைகளை பட்டியலாக (bullet points) வழங்கவும்.
4. பயிர் நிலை, கடைசியாக செய்த வேலை, மண்வகை ஆகியவற்றைக் கொண்டு இன்றைய தேவைகளை கணிக்கவும் (உதாரணமாக: பாசனம் செய்ய வேண்டிய நாள், உரம் இட வேண்டிய நேரம்)."""
        else:
            prompt = f"""You are a helpful agricultural assistant. Based on the farmer's profile and recent logs, provide a concise, proactive "Today's Suggested Tasks" brief.
            
Farmer Profile:
{profile_text}

Plot Details:
{plot_text}

Recent Observations / Logs:
{logs_text}

Current Month: {current_month}

CRITICAL: Output ONLY in English. Do NOT output Chinese characters, symbols, or any other languages. Respond STRICTLY in English.

Instructions:
1. Suggest 2-3 specific, actionable tasks the farmer should consider today (e.g. check soil moisture, consider crop fertilizer schedules).
2. Keep it concise, practical, and highly relevant to the crop stage inferred from past logs."""
    else:
        # Question-Answering mode
        if is_tamil:
            prompt = f"""நீ ஒரு விவசாய உதவியாளர். விவசாயியின் சுயவிவரம் மற்றும் குறிப்புகளின் அடிப்படையில் கீழே உள்ள கேள்விக்கு பதிலளிக்கவும்.
            
விவசாயி சுயவிவரம்:
{profile_text}

நிலத்தின் விபரங்கள்:
{plot_text}

கடந்த கால குறிப்புகள்:
{logs_text}

கேள்வி: "{question}"

விதிமுறைகள்:
1. தமிழ் மொழியில் மட்டும் பதிலளிக்கவும். தமிழ் மற்றும் ஆங்கில வார்த்தைகளைத் தவிர வேறு எழுத்துக்களையோ (சீன எழுத்துக்கள்) பயன்படுத்தவேண்டாம்.
2. கேள்விக்குத் தேவையான விபரங்களை மட்டுமே நேரடியாக விளக்கவும். வதந்திகளையோ தவறான பரிந்துரைகளையோ தவிர்க்கவும்."""
        else:
            prompt = f"""You are an agricultural assistant answering questions based on the farmer's history.
            
Farmer Profile:
{profile_text}

Plot Details:
{plot_text}

Field Observations History:
{logs_text}

User Question: "{question}"

CRITICAL: Output ONLY in English. Do NOT output Chinese characters or any other languages. Respond STRICTLY in English.

Instructions: Answer the question using the available context above. Keep the tone professional, helpful, and concise."""

    # Save user question to DB if not empty
    if question.strip():
        create_chat_message(db, current_user.id, req.plot_id, "user", question)

    response_text = _generate(prompt, max_new_tokens=300)

    # Save AI response to DB
    create_chat_message(db, current_user.id, req.plot_id, "ai", response_text)

    return {"response": response_text}


@router.post("/daily-brief")
def get_daily_brief(
    req: AIRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Daily brief is a simplified call to ask_ai with an empty question to trigger proactive suggestions
    req.question = ""
    return ask_ai(req, current_user, db)


@router.get("/chat-history", response_model=List[AIChatMessageResponse])
def get_history(
    plot_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_chat_history(db, current_user.id, plot_id)
