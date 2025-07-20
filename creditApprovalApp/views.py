from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer
from datetime import timedelta, date
from .utils import check_credit_eligibility
import logging

logger = logging.getLogger(__name__)

# /register
class RegisterCustomer(APIView):
    def post(self, request):
        try:
            data = request.data
            income = int(data['monthly_income'])
            # approved limit is 36% of monthly income rounded to the nearest lakh
            approved_limit = round((36 * income) / 100000) * 100000
            customer = Customer.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                age=data['age'],
                phone_number=data['phone_number'],
                monthly_salary=income,
                approved_limit=approved_limit,
            )
            return Response({
                "customer_id": customer.customer_id,
                "name": f"{customer.first_name} {customer.last_name}",
                "age": customer.age,
                "monthly_income": income,
                "approved_limit": approved_limit,
                "phone_number": customer.phone_number
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error in RegisterCustomer: {str(e)}")
            return Response({
                "error": "Failed to register customer",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# /check-eligibility
class CheckEligibility(APIView):
    def post(self, request):
        try:
            data = request.data
            
            # Check required fields
            required_fields = {'customer_id', 'loan_amount', 'tenure', 'interest_rate'}
            missing = [f for f in required_fields if f not in data]
            if missing:
                return Response(
                    {"error": f"Missing required fields: {', '.join(missing)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate and convert data types
            try:
                customer_id = int(data['customer_id'])
                loan_amount = float(data['loan_amount'])
                interest_rate = float(data['interest_rate'])
                tenure = int(data['tenure'])
            except (ValueError, TypeError) as e:
                return Response(
                    {"error": f"Invalid data types: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate ranges
            if loan_amount <= 0:
                return Response(
                    {"error": "Loan amount must be positive"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if tenure <= 0:
                return Response(
                    {"error": "Tenure must be positive"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if interest_rate < 0:
                return Response(
                    {"error": "Interest rate cannot be negative"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get customer
            try:
                customer = Customer.objects.get(customer_id=customer_id)
            except Customer.DoesNotExist:
                return Response({
                    "error": "Customer not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check eligibility 
            eligibility = check_credit_eligibility(customer, loan_amount, tenure, interest_rate)
            
            if not eligibility.get("approval"):
                return Response({
                    "customer_id": customer.customer_id,
                    "approval": False,
                    "message": eligibility.get("message", "Loan not approved"),
                    "credit_score": eligibility.get("credit_score", 0)
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "customer_id": customer.customer_id,
                "approval": True,
                "interest_rate": interest_rate,
                "corrected_interest_rate": eligibility.get("corrected_interest_rate"),
                "tenure": tenure,
                "monthly_installment": eligibility.get("monthly_installment"),
                "credit_score": eligibility.get("credit_score", 0)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in CheckEligibility: {str(e)}")
            return Response({
                "error": "Internal server error",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# /create-loan
class CreateLoan(APIView):
    def post(self, request):
        try:
            data = request.data

            # Check required fields
            required_fields = {'customer_id', 'loan_amount', 'tenure', 'interest_rate'}
            missing = [f for f in required_fields if f not in data]
            if missing:
                return Response(
                    {"error": f"Missing required fields: {', '.join(missing)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate and convert data types
            try:
                customer_id = int(data['customer_id'])
                loan_amount = float(data['loan_amount'])
                interest_rate = float(data['interest_rate'])
                tenure = int(data['tenure'])
            except (ValueError, TypeError) as e:
                return Response(
                    {"error": f"Invalid data types: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate ranges
            if loan_amount <= 0:
                return Response(
                    {"error": "Loan amount must be positive"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if tenure <= 0:
                return Response(
                    {"error": "Tenure must be positive"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if interest_rate < 0:
                return Response(
                    {"error": "Interest rate cannot be negative"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get customer
            try:
                customer = Customer.objects.get(customer_id=customer_id)
            except Customer.DoesNotExist:
                return Response({
                    "error": "Customer not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check eligibility 
            eligibility = check_credit_eligibility(customer, loan_amount, tenure, interest_rate)

            if not eligibility.get("approval"):
                return Response({
                    "loan_id": None,
                    "customer_id": customer.customer_id,
                    "loan_approved": False,
                    "message": eligibility.get("message", "Loan not approved"),
                    "credit_score": eligibility.get("credit_score", 0)
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create Loan
            start_date = date.today()
            end_date = start_date + timedelta(days=30 * tenure)

            loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount,
                tenure=tenure,
                interest_rate=eligibility.get("corrected_interest_rate"),
                monthly_repayment=eligibility.get("monthly_installment"),
                emis_paid_on_time=0,
                start_date=start_date,
                end_date=end_date,
            )

            # Update customer's current debt
            customer.current_debt += loan_amount
            customer.save()

            return Response({
                "loan_id": loan.loan_id,
                "customer_id": customer.customer_id,
                "loan_approved": True,
                "message": "Loan approved and created successfully",
                "monthly_repayment": eligibility.get("monthly_installment"),
                "corrected_interest_rate": eligibility.get("corrected_interest_rate")
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error in CreateLoan: {str(e)}")
            return Response({
                "error": "Internal server error",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# /view-loan/<loan_id>
class ViewLoan(APIView):
    def get(self, request, loan_id):
        try:
            # Get all past loans
            loan = Loan.objects.get(loan_id=loan_id)
            customer = loan.customer
            return Response({
                "loan_id": loan.loan_id,
                "customer": {
                    "id": customer.customer_id,
                    "first_name": customer.first_name,
                    "last_name": customer.last_name,
                    "phone_number": customer.phone_number,
                    "age": customer.age,
                },
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_repayment,
                "tenure": loan.tenure,
            }, status=status.HTTP_200_OK)
        except Loan.DoesNotExist:
            return Response({
                "error": "Loan not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in ViewLoan: {str(e)}")
            return Response({
                "error": "Internal server error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# /view-loans/<customer_id>
class ViewLoans(APIView):
    def get(self, request, customer_id):
        try:
            # Validate customer exists
            try:
                customer = Customer.objects.get(customer_id=customer_id)
            except Customer.DoesNotExist:
                return Response({
                    "error": "Customer not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            loans = Loan.objects.filter(customer=customer)
            response = []
            for loan in loans:
                repayments_left = max(0, loan.tenure - loan.emis_paid_on_time)
                response.append({
                    "loan_id": loan.loan_id,
                    "loan_amount": loan.loan_amount,
                    "interest_rate": loan.interest_rate,
                    "monthly_installment": loan.monthly_repayment,
                    "repayments_left": repayments_left,
                })
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in ViewLoans: {str(e)}")
            return Response({
                "error": "Internal server error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)