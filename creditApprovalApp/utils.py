from .models import Loan
from datetime import date

def calculate_emi(P, R, N):
    #Calculate EMI using the standard formula
    R = R / 12 / 100
    EMI = P * R * (1 + R) ** N / ((1 + R) ** N - 1)
    return round(EMI, 2)

def check_credit_eligibility(customer, loan_amount, tenure, interest_rate):
    #Check credit eligibility and return approval status with corrected rates

    score = 0
    # Get all past loans of the customer
    loans = Loan.objects.filter(customer=customer)
    corrected_rate = interest_rate
    
    # Check if current debt exceeds approved limit
    if customer.current_debt > customer.approved_limit:
        return {
            "approval": False,
            "credit_score": 0,
            "message": "Current debt exceeds approved limit"
        }

    if loans.exists():
        # Calculate on-time payment rate
        total_emis = sum([l.emis_paid_on_time for l in loans])
        total_loans = loans.count()
        on_time_rate = total_emis / max(total_loans, 1) if total_loans > 0 else 0
        
        if on_time_rate >= 0.8:
            score += 20
        if loans.filter(start_date__year=date.today().year).exists():
            score += 10
        if loans.count() < 3:
            score += 10
        if customer.current_debt <= customer.approved_limit:
            score += 10
    else:
        score += 20  # for fresh customers

    if score > 50:
        corrected_rate = interest_rate
        approval = True
    elif 30 < score <= 50:
        corrected_rate = max(interest_rate, 12)
        approval = True
    elif 10 < score <= 30:
        corrected_rate = max(interest_rate, 16)
        approval = True
    else:
        approval = False

    if not approval:
        return {
            "approval": False,
            "message": "Credit score too low",
            "credit_score": score
        }

    emi = calculate_emi(loan_amount, corrected_rate, tenure)

    if emi > 0.5 * customer.monthly_salary:
        return {
            "approval": False,
            "message": "EMI exceeds 50% of salary",
            "credit_score": score
        }

    return {
        "approval": True,
        "corrected_interest_rate": corrected_rate,
        "monthly_installment": emi,
        "credit_score": score
    }
