from sqlalchemy.orm import Session
from models.user_profile import UserProfile
from models.loan_eligibility import LoanEligibility
from repositories.credit_repository import CreditRepository
from repositories.eligibility_repository import EligibilityRepository

ANNUAL_INTEREST_RATE     = 12.0
ALLOWED_TENURES          = [3, 6, 9, 12]
PLATFORM_MAX_LOAN_AMOUNT = 20_000

CREDIT_SCORE_TIERS = [
    (800, 20_000),
    (750, 15_000),
    (700, 10_000),
    (650,  5_000),
]


def _get_tier_max_amount(credit_score: int) -> int:
    
    if credit_score >= 800:
        return 20_000
    elif credit_score >= 750:
        return 15_000
    elif credit_score >= 700:
        return 10_000
    elif credit_score >= 650:
        return 5_000
    else:
        return 0


def _monthly_rate() -> float:
    return (ANNUAL_INTEREST_RATE / 12) / 100


def calculate_emi(principal: float, tenure: int) -> float:
    r = _monthly_rate()
    if r == 0:
        return round(principal / tenure, 2)
    emi = (principal * r * (1 + r) ** tenure) / ((1 + r) ** tenure - 1)
    return round(emi, 2)


def generate_amortization_schedule(principal: float, tenure: int) -> list[dict]:
    r        = _monthly_rate()
    emi      = calculate_emi(principal, tenure)
    balance  = principal
    schedule = []

    for month in range(1, tenure + 1):
        interest_part  = round(balance * r, 2)
        principal_part = round(emi - interest_part, 2)
        balance        = round(balance - principal_part, 2)

        if month == tenure:
            principal_part = round(principal_part + balance, 2)
            balance        = 0.0

        schedule.append({
            "month":     month,
            "emi":       emi,
            "principal": principal_part,
            "interest":  interest_part,
            "balance":   max(balance, 0.0),
        })

    return schedule


def get_apr() -> float:
    return ANNUAL_INTEREST_RATE


class EligibilityService:

    @staticmethod
    def check_eligibility(
        db  : Session,
        user: UserProfile,
    ) -> LoanEligibility:
        credit_profile = CreditRepository.get_latest_credit_profile(db, user.user_id)
        if not credit_profile:
            credit_profile = CreditRepository.create_dummy_credit_profile(db, user.user_id)

        if not credit_profile:
            return EligibilityRepository.save_or_update_eligibility(
                db, user.user_id,
                eligibility_status = "REJECTED",
                failure_reason     = "CREDIT_PROFILE_NOT_FOUND",
            )
        credit_score   = credit_profile.credit_score
        bureau_name    = credit_profile.bureau_name
        existing_emi   = float(credit_profile.total_existing_emi or 0)
        monthly_income = float(user.monthly_income or 0)
        if credit_score >= 800:
            approved_amount = 20_000

        elif credit_score >= 750:
            approved_amount = 15_000

        elif credit_score >= 700:
            approved_amount = 10_000

        elif credit_score >= 650:
            approved_amount = 5_000

        else:
            return EligibilityRepository.save_or_update_eligibility(
                db, user.user_id,
                eligibility_status = "REJECTED",
                credit_profile_id  = credit_profile.id,
                credit_score_used  = credit_score,
                bureau_name        = bureau_name,
                income_used        = monthly_income,
                existing_emi       = existing_emi,
                failure_reason     = "LOW_CREDIT_SCORE",
            )
        return EligibilityRepository.save_or_update_eligibility(
            db, user.user_id,
            eligibility_status  = "ELIGIBLE",
            credit_profile_id   = credit_profile.id,
            credit_score_used   = credit_score,
            bureau_name         = bureau_name,
            income_used         = monthly_income,
            existing_emi        = existing_emi,
            max_eligible_amount = approved_amount,
        )

        # ── FOIR check (reserved for future activation) ───────────────────────
        # MAX_FOIR = 0.50
        #
        # if monthly_income <= 0:
        #     return EligibilityRepository.save_or_update_eligibility(
        #         db, user.user_id,
        #         eligibility_status = "REJECTED",
        #         failure_reason     = "INVALID_INCOME",
        #     )
        #
        # max_total_emi        = monthly_income * MAX_FOIR
        # max_new_emi_capacity = max_total_emi - existing_emi
        #
        # if max_new_emi_capacity <= 0:
        #     return EligibilityRepository.save_or_update_eligibility(
        #         db, user.user_id,
        #         eligibility_status = "REJECTED",
        #         credit_profile_id  = credit_profile.id,
        #         income_used        = monthly_income,
        #         existing_emi       = existing_emi,
        #         credit_score_used  = credit_score,
        #         bureau_name        = bureau_name,
        #         failure_reason     = "NO_EMI_CAPACITY",
        #     )
        #
        # foir_based_max      = calculate_principal_from_emi(max_new_emi_capacity, tenure)
        # max_eligible_amount = min(approved_amount, foir_based_max)
        # proposed_emi        = calculate_emi(max_eligible_amount, tenure)
        # foir                = round((existing_emi + proposed_emi) / monthly_income, 4)
        #
        # if foir > MAX_FOIR:
        #     return EligibilityRepository.save_or_update_eligibility(
        #         db, user.user_id,
        #         eligibility_status  = "REJECTED",
        #         credit_profile_id   = credit_profile.id,
        #         income_used         = monthly_income,
        #         existing_emi        = existing_emi,
        #         proposed_emi        = proposed_emi,
        #         foir_ratio          = foir,
        #         credit_score_used   = credit_score,
        #         bureau_name         = bureau_name,
        #         max_eligible_amount = max_eligible_amount,
        #         failure_reason      = "FOIR_EXCEEDED",
        #     )