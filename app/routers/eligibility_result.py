from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from services.eligibility_service import (
    ALLOWED_TENURES,
    PLATFORM_MAX_LOAN_AMOUNT,
    CREDIT_SCORE_TIERS,
    get_apr,
)
from core.database import get_db
from models.loan_eligibility import LoanEligibility
from schemas.eligibility_result import (
    EligibilityResultResponseExtended,
    CreditSummary,
    CreditScoreTier,
)
from Utils.eligibility_messages import map_failure_reason

router = APIRouter()


@router.get("/{user_id}", response_model=EligibilityResultResponseExtended)
def get_eligibility_result(user_id: int, db: Session = Depends(get_db)):
    """
    Returns the saved eligibility result for a user.
    NOTE: EMI calculation and amortization schedule are NOT shown here.
            Use POST /loan/calculate with user_id + tenure_months to get
            full EMI breakdown, APR, and amortization schedule.
    """
    record: LoanEligibility = (
        db.query(LoanEligibility)
        .filter(LoanEligibility.user_id == user_id)
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail="No eligibility record found. Please run an eligibility check first."
        )

    status  = record.eligibility_status
    message = map_failure_reason(record.failure_reason, status)

    credit_summary = CreditSummary(
        currentScore  = record.credit_score_used,
        previousScore = record.previous_credit_score_used,
        bureau        = record.bureau_name,
    )

    credit_score_tiers = [
        CreditScoreTier(
            minScore      = score,
            maxLoanAmount = amount,
            label         = f"₹{amount:,}"
        )
        for score, amount in CREDIT_SCORE_TIERS
    ]
    if status == "REJECTED":
        return EligibilityResultResponseExtended(
            status                  = status,
            message                 = message,
            maxEligibleAmount       = 0.0,
            maxAffordableEmi        = float(record.max_eligible_emi or 0),
            platformMaxLoanAmount   = float(PLATFORM_MAX_LOAN_AMOUNT),
            platformProvidedTenures = ALLOWED_TENURES,
            annualInterestRate      = get_apr(),
            failureReason           = record.failure_reason,
            creditScoreTiers        = credit_score_tiers,
            creditSummary           = credit_summary,
            evaluatedAt             = record.latest_checked_at,
            previouslyCheckedAt     = record.previously_checked_at,
        )
    max_eligible_amount = min(
        float(record.max_eligible_amount or 0),
        float(PLATFORM_MAX_LOAN_AMOUNT),
    )

    return EligibilityResultResponseExtended(
        status                  = status,
        message                 = message,
        maxEligibleAmount       = max_eligible_amount,
        maxAffordableEmi        = float(record.max_eligible_emi or 0),
        platformMaxLoanAmount   = float(PLATFORM_MAX_LOAN_AMOUNT),
        platformProvidedTenures = ALLOWED_TENURES,
        annualInterestRate      = get_apr(),
        failureReason           = None,
        creditScoreTiers        = credit_score_tiers,
        creditSummary           = credit_summary,
        evaluatedAt             = record.latest_checked_at,
        previouslyCheckedAt     = record.previously_checked_at,
    )
