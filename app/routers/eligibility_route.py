from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from models.user_profile import UserProfile
from services.eligibility_service import (
    EligibilityService,
    ALLOWED_TENURES,
    PLATFORM_MAX_LOAN_AMOUNT,
    CREDIT_SCORE_TIERS,
    get_apr,
)

router = APIRouter()


@router.post("/check/{user_id}")
def check_loan_eligibility(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Credit Score → Approved Amount:
        >= 800  →  ELIGIBLE  →  ₹20,000
        >= 750  →  ELIGIBLE  →  ₹15,000
        >= 700  →  ELIGIBLE  →  ₹10,000
        >= 650  →  ELIGIBLE  →  ₹5,000
         < 650  →  REJECTED

    NOTE: EMI calculation and amortization schedule are NOT returned here.
          Use POST /loan/calculate with user_id + tenure_months to get
          full EMI breakdown, APR, and amortization schedule.
    """
    user: UserProfile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        eligibility = EligibilityService.check_eligibility(db=db, user=user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    status = eligibility.eligibility_status
    if status == "REJECTED":
        return {
            "user_id":            user_id,
            "eligibility_status": status,
            "failure_reason":     eligibility.failure_reason,
            "credit_summary": {
                "current_score": eligibility.credit_score_used,
                "bureau":        eligibility.bureau_name,
            },
            "credit_score_tiers": [
                {"min_score": score, "max_loan_amount": amount}
                for score, amount in CREDIT_SCORE_TIERS
            ],
            "Message": "Unfortunately, you are not eligible for a loan based on your current credit score. Please review the credit score tiers and consider improving your credit profile to become eligible in the future.",
        }
    approved_amount = float(eligibility.max_eligible_amount or 0)

    return {
        "user_id":            user_id,
        "eligibility_status": status,
        "loan_offer": {
            "approved_amount":      approved_amount,
            "annual_interest_rate": get_apr(),
            "available_tenures":    ALLOWED_TENURES,
            "platform_max_amount":  PLATFORM_MAX_LOAN_AMOUNT,
        },
        "credit_summary": {
            "current_score":  eligibility.credit_score_used,
            "previous_score": eligibility.previous_credit_score_used,
            "bureau":         eligibility.bureau_name,
        },
        "Message": "Congratulations! You are eligible for a loan. Please proceed to calculate your EMI based on your approved amount and preferred tenure.",
    }