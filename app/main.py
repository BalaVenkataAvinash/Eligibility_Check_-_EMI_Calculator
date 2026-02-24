from fastapi import FastAPI
from core.database import engine, Base
from models import (
    user_profile,
    dummy_pan,
    kyc_pan,
    credit_profile,
    credit_account,
    loan_eligibility,
    loan_calculation,
)  
from routers import user_profile
from routers.credit_route import router as credit_router
from routers.eligibility_route import router as eligibility_router
from routers.eligibility_result import router as eligibility_result_router
from routers.loan_calculator_route import router as loan_calculator_router
from routers.loan_calculator_result import router as loan_router

app = FastAPI(title="Loan Service Provider API")
Base.metadata.create_all(bind=engine)

app.include_router(user_profile.router, prefix="/users", tags=["Users"])
app.include_router(credit_router, prefix="/api/v1/credit", tags=["Credit Profile"])
app.include_router(eligibility_router, prefix="/api/v1/eligibility", tags=["Loan Eligibility"])
app.include_router(eligibility_result_router, prefix="/api/v1/eligibility-result", tags=["Loan Eligibility"])
app.include_router(loan_calculator_router, prefix="/api/v1/loan", tags=["Loan Calculator"])
app.include_router(loan_router, prefix="/api/v1/loan", tags=["Loan Calculator"])


@app.get("/")
def root():
    return {"status": "LSP backend running"}