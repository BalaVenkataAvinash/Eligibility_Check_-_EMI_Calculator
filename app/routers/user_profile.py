from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.user_profile_sch import UserProfileCreateSchema
from services.user_profile_service import create_user_profile

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_profile(payload: UserProfileCreateSchema, db: Session = Depends(get_db)):
    """Create a new user profile only if PAN exists.

    If PAN is present, the user's `pan_status` will be set to VERIFIED and
    a KYC PAN record will be added to `kyc_pan_verifications` table.
    """
    try:
        user = create_user_profile(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {"user_id": user.user_id, "pan_status": user.pan_status}
