"""
SAATHI What-If Scenario Simulation API Router
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.simulation import SimulationRequest, SimulationResponse
from backend.app.services.simulation_service import SimulationService
from backend.app.core.permissions import get_current_user, require_role
from backend.app.core.rate_limit import rate_limit
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/simulations", tags=["What-If Simulations"])

@router.post("/personnel/{personnel_id}", response_model=SimulationResponse, dependencies=[Depends(require_role("WELFARE_OFFICER", "ADMIN")), Depends(rate_limit(max_requests=60, window_seconds=60))])
def run_scenario_simulation(
    personnel_id: str,
    simulation: SimulationRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Project model response under hypothetical operational changes (e.g., reducing night shifts, granting rest days).
    Clearly labeled as scenario simulation; does not persist or modify actual personnel history.
    """
    role = current_user.roles[0].name if current_user.roles else "WELFARE_OFFICER"
    client_ip = request.client.host if request.client else None
    try:
        resp = SimulationService.simulate_adjustments(
            db=db,
            personnel_id=personnel_id,
            user_id=current_user.id,
            username=current_user.username,
            role=role,
            simulation=simulation,
            ip_address=client_ip
        )
        return resp
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Simulation computation error for {personnel_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Simulation service encountered an unexpected error. Please check system audit logs.")
