from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date
 
class UserProfileCreateSchema(BaseModel):
    full_name: str
    dob: date
    address: str
    email: EmailStr
    employment_type: str
    monthly_income: float
    pan_number: str = Field(..., min_length=9, max_length=9, pattern=r"^[A-Z]{4}[0-9]{4}[A-Z]{1}$")
    aadhaar_number: str = Field(..., min_length=12, max_length=12, pattern=r"^[0-9]{12}$")
 
class UserProfileUpdateSchema(BaseModel):
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    employment_type: Optional[str] = None
    monthly_income: Optional[float] = None
 
