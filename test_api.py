import requests

url = "http://127.0.0.1:5000/predict"

sample = {
    "annual_income": 50000,
    "debt_to_income_ratio": 0.25,
    "credit_score": 700,
    "loan_amount": 10000,
    "interest_rate": 0.08,
    "gender": "Male",
    "marital_status": "Single",
    "education_level": "Bachelor",
    "employment_status": "Employed",
    "loan_purpose": "Debt Consolidation",
    "grade_subgrade": "B2"
}

response = requests.post(url, json=sample)
print(response.json())
