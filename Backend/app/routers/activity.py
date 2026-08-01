from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..auth import get_current_user
from ..models import User
from ..schemas import ActivityLogCreate, ActivityLogResponse
from ..crud import create_activity_log, get_activity_logs

router = APIRouter(prefix="/api/activity-log", tags=["activity-log"])


@router.post("", response_model=ActivityLogResponse, status_code=status.HTTP_201_CREATED)
def create_entry(
    activity_in: ActivityLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_activity_log(db, current_user.id, activity_in)


@router.get("", response_model=List[ActivityLogResponse])
def list_entries(
    plot_id: Optional[str] = None,
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Parse dates if provided
    start_dt = None
    end_dt = None
    try:
        if date_start:
            start_dt = datetime.fromisoformat(date_start)
        if date_end:
            end_dt = datetime.fromisoformat(date_end)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use ISO format (e.g. YYYY-MM-DD)."
        )

    return get_activity_logs(db, current_user.id, plot_id, start_dt, end_dt)
