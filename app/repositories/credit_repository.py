from datetime import datetime
from sqlalchemy.orm import Session

from models.credit_profile import CreditProfile
from models.credit_account import CreditAccount


class CreditRepository:

    @staticmethod
    def get_latest_credit_profile(db: Session, user_id: str) -> CreditProfile | None:
        return (
            db.query(CreditProfile)
            .filter(CreditProfile.user_id == user_id)
            .order_by(CreditProfile.pulled_at.desc())
            .first()
        )

    @staticmethod
    def create_dummy_credit_profile(db: Session, user_id: str) -> CreditProfile:
        """
        #
        # @staticmethod
        # def create_from_transunion(
        #     db: Session,
        #     user_id: str,
        #     pan_number: str
        # ) -> CreditProfile:
        #
        #     import requests, os
        #
        #     url     = "https://api.transunion.com/v1/credit-report"
        #     headers = {
        #         "Authorization": f"Bearer {os.getenv('TRANSUNION_API_KEY')}",
        #         "Content-Type":  "application/json",
        #     }
        #     payload = {
        #         "pan":     pan_number,
        #         "consent": True,
        #         "purpose": "LOAN_UNDERWRITING",
        #     }
        #
        #     resp = requests.post(url, json=payload, headers=headers, timeout=10)
        #     resp.raise_for_status()
        #     data = resp.json()
        #
        #     # ── Parse accounts from bureau response ───────────────────────────
        #     raw_accounts = data.get("accounts", [])
        #     active_accounts = [a for a in raw_accounts if a["status"] == "ACTIVE"]
        #     total_existing_emi = sum(float(a["emiAmount"]) for a in active_accounts)
        #
        #     # ── Persist CreditProfile ─────────────────────────────────────────
        #     profile = CreditProfile(
        #         user_id             = user_id,
        #         bureau_name         = data.get("bureau", "TransUnion"),
        #         credit_score        = data["creditScore"],
        #         report_reference_id = data.get("reportId"),
        #         total_active_loans  = len(active_accounts),
        #         total_existing_emi  = total_existing_emi,
        #         bureau_raw_response = data,              # store full response for audit
        #         pulled_at           = datetime.utcnow(),
        #     )
        #     db.add(profile)
        #     db.flush()   # get profile.id before inserting child accounts
        #
        #     for acc in raw_accounts:
        #         db.add(CreditAccount(
        #             credit_profile_id = profile.id,
        #             loan_type         = acc.get("loanType"),
        #             emi_amount        = float(acc.get("emiAmount", 0)),
        #             status            = acc.get("status"),
        #         ))
        #
        #     db.commit()
        #     db.refresh(profile)
        #     return profile
        #
        """
        import random

        dummy_score = random.choice([620, 670, 710, 760, 810])

        # Build realistic dummy accounts
        dummy_accounts_map = {
            620: [{"loan_type": "PL", "emi_amount": 4000, "status": "ACTIVE"},
                  {"loan_type": "CC", "emi_amount": 2000, "status": "ACTIVE"}],
            670: [{"loan_type": "PL", "emi_amount": 2000, "status": "ACTIVE"}],
            710: [{"loan_type": "AUTO", "emi_amount": 3500, "status": "ACTIVE"}],
            760: [{"loan_type": "HL",   "emi_amount": 5000, "status": "ACTIVE"},
                  {"loan_type": "PL",   "emi_amount": 1000, "status": "CLOSED"}],
            810: [],  # no existing obligations — best case
        }

        accounts_data = dummy_accounts_map.get(dummy_score, [])
        active_accounts = [a for a in accounts_data if a["status"] == "ACTIVE"]
        total_existing_emi = sum(a["emi_amount"] for a in active_accounts)

        profile = CreditProfile(
            user_id             = user_id,
            bureau_name         = "TransUnion (Dummy)",
            credit_score        = dummy_score,
            report_reference_id = f"DUMMY-{str(user_id)[:8].upper()}",
            total_active_loans  = len(active_accounts),
            total_existing_emi  = total_existing_emi,
            bureau_raw_response = {"dummy": True, "score": dummy_score},
            pulled_at           = datetime.utcnow(),
        )
        db.add(profile)
        db.flush()
        for acc in accounts_data:
            db.add(CreditAccount(
                credit_profile_id = profile.id,
                loan_type         = acc["loan_type"],
                emi_amount        = acc["emi_amount"],
                status            = acc["status"],
            ))

        db.commit()
        db.refresh(profile)
        return profile