# Loan Service Provider (LSP)

> A FastAPI-based microservice for **Loan Eligibility Check** and **EMI Calculator** modules, integrated with TransUnion API for real-time credit scoring.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Modules](#modules)
- [Eligibility Criteria](#eligibility-criteria)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Environment Variables](#environment-variables)
- [Tech Stack](#tech-stack)

---

## Project Overview

The **Loan Service Provider (LSP)** system enables users to:
1. Create a user profile and get assessed for loan eligibility based on their credit score.
2. Calculate EMI (Equated Monthly Installment) for the eligible loan amount with a full amortization schedule.

---

## Modules

### 1. Eligibility Check Module
Determines whether a user is eligible for a loan and the maximum loan amount they qualify for, based on their credit score fetched from the **TransUnion API**.

### 2. EMI Calculator Module
Calculates the monthly EMI for the eligible loan amount based on a user-specified tenure, and returns a detailed **amortization schedule**.


## Eligibility Criteria

| Credit Score Range | Loan Eligibility | Status |
|--------------------|-----------------|--------|
| Below 650          | ₹0              | Rejected |
| 650 – 699          | ₹5,000          | Eligible |
| 700 – 749          | ₹10,000         | Eligible |
| 750 – 799          | ₹15,000         | Eligible |
| 800 and above      | ₹20,000         | Eligible |

> **Credit Score Source:** TransUnion API (fetched using the user's PAN card number)

---

## API Endpoints

### User Profile

1. User Profile Creation:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/users/` | Create a new user profile |

### Credit Score

2. Generate the Credit Score for the user by there Pan Details in the profile:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/credit/generate/{user_id}` | Generate Credit Profile by the `user_id` |

3. Get the credit score which are generated:

| `GET`  | `/api/v1/credit/{user_id}` | Get Credit Profile |

### Eligibility Check

4. Check the loan eligibility based on the credit score:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/eligibility/check/{user_id}` | Trigger eligibility check using `user_id` |

5. Get the eligibility result and eligibility amount of the specific user by the user_id:

| `GET`  | `/api/v1/eligibility-result/{user_id}` | Get eligibility result for a user |

### EMI Calculator

6. Calculate the emi for the user as the eligibility amount act as the principle amount:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/loan/calculate` | Calculate EMI using `user_id` + `tenure_months` |

7. Get the calculated emi for the specific user:

| `GET`  | `/api/v1/loan/result/{user_id}` | Get EMI & amortization schedule by user ID |

---

### Sample Request & Response

#### POST `/eligibility/check`
```json
{
  "user_id": "1"
}
```
#### Response
```json
{
  "user_id": 1,
  "eligibility_status": "ELIGIBLE",
  "loan_offer": {
    "approved_amount": 10000,
    "annual_interest_rate": 12,
    "available_tenures": [
      3,
      6,
      9,
      12
    ],
    "platform_max_amount": 20000
  },
  "credit_summary": {
    "current_score": 710,
    "previous_score": 620,
    "bureau": "TransUnion (Dummy)"
  },
  "previously_checked_at": "2026-02-24T04:49:54.703900",
  "Message": "Congratulations! You are eligible for a loan. Please proceed to calculate your EMI based on your approved amount and preferred tenure."
}
```
#### POST `/loan/calculate`

#### Response
```json
{
  "status": "success",
  "message": "EMI calculated and saved successfully.",
  "data": {
    "id": 1,
    "user_id": 1,
    "eligible_amount": 10000,
    "requested_amount": 10000,
    "tenure_months": 6,
    "interest_rate_pa": 12,
    "monthly_emi": 1725.48,
    "total_repayment": 10352.88,
    "total_interest": 352.88,
    "status": "CHECKED",
    "amortization_schedule": [
      {
        "month": 1,
        "emi": 1725.48,
        "principal": 1625.48,
        "interest": 100,
        "balance": 8374.52
      },
      {
        "month": 2,
        "emi": 1725.48,
        "principal": 1641.73,
        "interest": 83.75,
        "balance": 6732.79
      },
      {
        "month": 3,
        "emi": 1725.48,
        "principal": 1658.15,
        "interest": 67.33,
        "balance": 5074.64
      },
      {
        "month": 4,
        "emi": 1725.48,
        "principal": 1674.73,
        "interest": 50.75,
        "balance": 3399.91
      },
      {
        "month": 5,
        "emi": 1725.48,
        "principal": 1691.48,
        "interest": 34,
        "balance": 1708.43
      },
      {
        "month": 6,
        "emi": 1725.48,
        "principal": 1708.43,
        "interest": 17.08,
        "balance": 0
      }
    ]
  }
}
```

---

## Project Structure

```
LSP_PROJECT/
├── app/
│   ├── core/
│   │   ├── config.py                  # App configuration
│   │   └── database.py                # DB connection setup
│   │
│   ├── models/
│   │   ├── credit_account.py
│   │   ├── credit_profile.py
│   │   ├── dummy_pan.py
│   │   ├── kyc_pan.py
│   │   ├── loan_calculation.py        # EMI & amortization model
│   │   ├── loan_eligibility.py        # Eligibility result model
│   │   └── user_profile.py            # User profile model
│   │
│   ├── repositories/
│   │   ├── credit_repository.py
│   │   ├── eligibility_repository.py  # Eligibility DB operations
│   │   ├── loan_calculator_repo.py    # EMI DB operations
│   │   └── user_repository.py         # User profile DB operations
│   │
│   ├── routers/
│   │   ├── credit_route.py
│   │   ├── eligibility_result.py
│   │   ├── eligibility_route.py       # Eligibility API routes
│   │   ├── loan_calculator_result.py
│   │   ├── loan_calculator_route.py   # EMI API routes
│   │   └── user_profile.py            # User profile routes
│   │
│   ├── schemas/
│   │   ├── credit_profile_sch.py
│   │   ├── eligibility_result.py
│   │   ├── eligibility.py             # Eligibility request/response schema
│   │   └── user_profile_sch.py        # User profile schema
│   │
│   ├── services/
│   │   ├── credit_service.py
│   │   ├── eligibility_service.py     # Eligibility business logic
│   │   ├── loan_service.py            # EMI calculation logic
│   │   └── user_profile_service.py    # User profile service
│   │
│   └── Utils/
│       ├── eligibility_messages.py    # Eligibility response messages
│       └── dummy_pan_data.py          # Mock PAN data for testing
│
├── main.py                            # FastAPI app entry point
├── .env                               # Environment variables
├── requirements.txt                   # Python dependencies
└── README.md
```

---

## Installation & Setup


# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload

```

Access the API docs at: `http://localhost:8000/docs`

---

## Environment Variables

```
.env
DATABASE_URL=postgresql://user:password@localhost:5432/lsp_db
TRANSUNION_API_URL=https://api.transunion.com/v1/credit-score
TRANSUNION_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI |
| Language | Python 3.10+ |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Credit API | TransUnion API |
| Validation | Pydantic |
| Server | Uvicorn |

---

## EMI Formula

```
EMI = [P × R × (1+R)^N] / [(1+R)^N - 1]

Where:
  P = Principal loan amount (eligible amount)
  R = Monthly interest rate (Annual Rate / 12 / 100)
  N = Tenure in months
```

---

**Loan Service Provider Team**  
Module: Eligibility Check & EMI Calculator