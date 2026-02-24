from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from repositories.credit_repository import CreditRepository
from models.credit_profile import CreditProfile

router = APIRouter()


@router.post("/generate/{user_id}")
def generate_credit_profile(
    user_id: int,
    force_refresh: bool = Query(
        default=False,
        description="If True, generates a new dummy profile even if one already exists"
    ),
    db: Session = Depends(get_db),
):
    """
    Note:
        The eligibility check also auto-generates a dummy profile if one
        doesn't exist, so calling this manually is optional.
    """

    existing = CreditRepository.get_latest_credit_profile(db, user_id)

    if existing and not force_refresh:
        return {
            "message":           "Credit profile already exists. Use ?force_refresh=true to regenerate.",
            "credit_profile_id": existing.id,
            "credit_score":      existing.credit_score,
            "bureau_name":       existing.bureau_name,
            "total_active_loans": existing.total_active_loans,
            "total_existing_emi": float(existing.total_existing_emi or 0),
            "pulled_at":         existing.pulled_at,
            "expires_at":        existing.expires_at,
            "accounts": [
                {
                    "loan_type":  acc.loan_type,
                    "emi_amount": float(acc.emi_amount or 0),
                    "status":     acc.status,
                }
                for acc in existing.accounts
            ]
        }

    try:
        profile: CreditProfile = CreditRepository.create_dummy_credit_profile(
            db=db,
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate credit profile: {str(e)}"
        )

    return {
        "message":            "Dummy credit profile created successfully",
        "credit_profile_id":  profile.id,
        "credit_score":       profile.credit_score,
        "bureau_name":        profile.bureau_name,
        "total_active_loans": profile.total_active_loans,
        "total_existing_emi": float(profile.total_existing_emi or 0),
        "pulled_at":          profile.pulled_at,
        "expires_at":         profile.expires_at,
        "accounts": [
            {
                "loan_type":  acc.loan_type,
                "emi_amount": float(acc.emi_amount or 0),
                "status":     acc.status,
            }
            for acc in profile.accounts
        ]
    }


@router.get("/{user_id}")
def get_credit_profile(user_id: int, db: Session = Depends(get_db)):
    """
    Returns the latest credit profile for a user.
    Useful for verifying what data the eligibility check will use.
    """
    profile = CreditRepository.get_latest_credit_profile(db, user_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="No credit profile found for this user. Call POST /credit/generate/{user_id} first."
        )

    return {
        "credit_profile_id":  profile.id,
        "credit_score":       profile.credit_score,
        "bureau_name":        profile.bureau_name,
        "total_active_loans": profile.total_active_loans,
        "total_existing_emi": float(profile.total_existing_emi or 0),
        "pulled_at":          profile.pulled_at,
        "expires_at":         profile.expires_at,
        "accounts": [
            {
                "loan_type":  acc.loan_type,
                "emi_amount": float(acc.emi_amount or 0),
                "status":     acc.status,
            }
            for acc in profile.accounts
        ]
    }