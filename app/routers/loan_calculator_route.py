from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.database import get_db
from services.loan_service import LoanCalculationService, ALLOWED_TENURES

router = APIRouter()


class LoanCalculateRequest(BaseModel):
    """
    Input payload for EMI calculation.
    Note:
        The loan amount is NOT provided by the user. It is automatically
        fetched from the loan_eligibility table (max_eligible_amount).
        EMI is always calculated on the user's full eligible amount.
    """
    user_id       : int
    tenure_months : int = Field(
        ...,
        description=f"Tenure in months. Allowed: {ALLOWED_TENURES}",
    )


@router.post("/calculate")
def calculate_emi(
    payload: LoanCalculateRequest,
    db: Session = Depends(get_db),
):
    try:
        result = LoanCalculationService.calculate_and_save(
            db            = db,
            user_id       = payload.user_id,
            tenure_months = payload.tenure_months,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    record = result["record"]

    return {
        "status":  "success",
        "message": "EMI calculated and saved successfully.",
        "data": {
            "id":                    record.id,
            "user_id":               record.user_id,
            "eligible_amount":       record.eligible_amount,
            "requested_amount":      record.requested_amount,
            "tenure_months":         record.tenure_months,
            "interest_rate_pa":      record.interest_rate_pa,
            "monthly_emi":           record.monthly_emi,
            "total_repayment":       record.total_repayment,
            "total_interest":        record.total_interest,
            # "apr":                   result["apr"],
            "status":                record.status,
            "amortization_schedule": result["amortization_schedule"],
        },
    }
