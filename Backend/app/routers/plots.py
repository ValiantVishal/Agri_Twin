from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from ..database import get_db
from ..auth import get_current_user
from ..models import User, Plot
from ..schemas import PlotCreate, PlotUpdate, PlotResponse
from ..crud import get_plot, get_plots_by_farmer, create_plot, update_plot, soft_delete_plot
from ..services.geo_utils import is_polygon_valid, calculate_area_and_perimeter

router = APIRouter(prefix="/api/plots", tags=["plots"])


class PlotCreateResponse(BaseModel):
    plot: PlotResponse
    warning: Optional[str] = None


@router.post("", response_model=PlotCreateResponse, status_code=status.HTTP_201_CREATED)
def sync_or_create_plot(
    plot_in: PlotCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check for idempotence using client-generated UUID
    existing_plot = db.query(Plot).filter(Plot.id == plot_in.id).first()
    if existing_plot:
        if existing_plot.farmer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this plot."
            )
        # Return existing plot (idempotent response)
        # Check if active
        if not existing_plot.is_active:
            existing_plot.is_active = True
            db.commit()
            db.refresh(existing_plot)
        return PlotCreateResponse(plot=PlotResponse.from_orm(existing_plot))

    # Validate polygon geometry (minimum 3 coordinates and must not self-intersect)
    points_dict = [{"lat": p.lat, "lng": p.lng} for p in plot_in.points]
    if not is_polygon_valid(points_dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid polygon structure. Check for self-intersections or duplicate points."
        )

    # Server-side calculation of area & perimeter
    srv_area_sqm, srv_area_acres, srv_area_cents, srv_perimeter_m = calculate_area_and_perimeter(points_dict)

    # GPS Drift Warning comparison (tolerance of 5% difference in area)
    warning = None
    if plot_in.area_sqm > 0:
        difference = abs(srv_area_sqm - plot_in.area_sqm) / plot_in.area_sqm
        if difference > 0.05:
            warning = (
                f"Significant area discrepancy detected (GPS drift). "
                f"Client: {plot_in.area_acres:.2f} acres, Server: {srv_area_acres:.2f} acres."
            )

    # Use server-calculated values as the source of truth
    plot_data = {
        "id": plot_in.id,
        "plot_name": plot_in.plot_name,
        "points": [p.dict() for p in plot_in.points],
        "area_sqm": srv_area_sqm,
        "area_acres": srv_area_acres,
        "area_cents": srv_area_cents,
        "perimeter_m": srv_perimeter_m
    }

    new_plot = create_plot(db, plot_data, farmer_id=current_user.id)
    return PlotCreateResponse(plot=PlotResponse.from_orm(new_plot), warning=warning)


@router.get("", response_model=List[PlotResponse])
def list_plots(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plots = get_plots_by_farmer(db, current_user.id)
    return [PlotResponse.from_orm(p) for p in plots]


@router.get("/{plot_id}", response_model=PlotResponse)
def get_single_plot(
    plot_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plot = get_plot(db, plot_id)
    if not plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plot not found."
        )
    if plot.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this plot."
        )
    return PlotResponse.from_orm(plot)


@router.put("/{plot_id}", response_model=PlotResponse)
def update_existing_plot(
    plot_id: str,
    plot_update: PlotUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_plot = get_plot(db, plot_id)
    if not db_plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plot not found."
        )
    if db_plot.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this plot."
        )

    update_dict = {}
    if plot_update.plot_name is not None:
        update_dict["plot_name"] = plot_update.plot_name

    if plot_update.points is not None:
        points_dict = [{"lat": p.lat, "lng": p.lng} for p in plot_update.points]
        if not is_polygon_valid(points_dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid polygon structure. Check for self-intersections."
            )
        # Recalculate based on new points
        srv_area_sqm, srv_area_acres, srv_area_cents, srv_perimeter_m = calculate_area_and_perimeter(points_dict)
        update_dict["points"] = [p.dict() for p in plot_update.points]
        update_dict["area_sqm"] = srv_area_sqm
        update_dict["area_acres"] = srv_area_acres
        update_dict["area_cents"] = srv_area_cents
        update_dict["perimeter_m"] = srv_perimeter_m

    updated = update_plot(db, db_plot, update_dict)
    return PlotResponse.from_orm(updated)


@router.delete("/{plot_id}")
def delete_plot(
    plot_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_plot = get_plot(db, plot_id)
    if not db_plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plot not found."
        )
    if db_plot.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this plot."
        )
    soft_delete_plot(db, db_plot)
    return {"message": "Plot deleted successfully"}
