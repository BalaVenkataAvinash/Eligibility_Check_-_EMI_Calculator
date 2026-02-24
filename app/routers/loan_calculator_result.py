from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from services.loan_service import LoanCalculationService

router = APIRouter()
@router.get("/result/{user_id}")
def get_loan_calculation(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Fetches the saved EMI calculation for a user.

    Returns the most recent calculation stored in loan_calculations.
    
    """
    record = LoanCalculationService.get_calculation(db, user_id)

    if not record:
        raise HTTPException(
            status_code=404,
            detail=(
                "No EMI calculation found for this user. "
                "Please use POST /loan/calculate to calculate first."
            ),
        )

    return {
        "status": "success",
        "data": {
            "id":      record.id,
            "user_id": record.user_id,
            "requested_amount": record.requested_amount,
            "eligible_amount":  record.eligible_amount,
            "tenure_months":    record.tenure_months,
            "interest_rate_pa": record.interest_rate_pa,
            "monthly_emi":      record.monthly_emi,
            "total_repayment":  record.total_repayment,
            "total_interest":   record.total_interest,
            "status":                record.status,
        },
    }