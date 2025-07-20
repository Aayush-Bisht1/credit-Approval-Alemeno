import pandas as pd
from django.core.management.base import BaseCommand
from creditApprovalApp.models import Customer, Loan
from datetime import datetime


class Command(BaseCommand):
    help = 'Load customer and loan data from Excel files'

    def handle(self, *args, **kwargs):
        # Load Excel files
        customer_df = pd.read_excel('customer_data.xlsx')
        loan_df = pd.read_excel('loan_data.xlsx')

        # Rename column headers to match model field names
        customer_df = customer_df.rename(columns={
            'Customer ID': 'customer_id',
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Phone Number': 'phone_number',
            'Monthly Salary': 'monthly_salary',
            'Approved Limit': 'approved_limit',
            'Age': 'age',
            'Current Debt': 'current_debt' 
        })

        loan_df = loan_df.rename(columns={
            'Loan ID': 'loan_id',
            'Customer ID': 'customer_id',
            'Loan Amount': 'loan_amount',
            'Tenure': 'tenure',
            'Interest Rate': 'interest_rate',
            'Monthly payment': 'monthly_repayment',
            'EMIs paid on Time': 'emis_paid_on_time',
            'Date of Approval': 'start_date',
            'End Date': 'end_date',
        })

        for _, row in customer_df.iterrows():
            Customer.objects.update_or_create(
                customer_id=row['customer_id'],
                defaults={
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'phone_number': str(row['phone_number']),
                    'monthly_salary': int(row['monthly_salary']),
                    'approved_limit': int(row['approved_limit']),
                    'age': int(row.get('age', 0)),
                    'current_debt': int(row.get('current_debt', 0)),
                }
            )

        for _, row in loan_df.iterrows():
            customer = Customer.objects.get(customer_id=row['customer_id'])

            Loan.objects.update_or_create(
                loan_id=row['loan_id'],
                defaults={
                    'customer_id': customer, 
                    'loan_amount': float(row['loan_amount']),
                    'tenure': int(row['tenure']),
                    'interest_rate': float(row['interest_rate']),
                    'monthly_repayment': float(row['monthly_repayment']),
                    'emis_paid_on_time': int(row['emis_paid_on_time']),
                    'start_date': pd.to_datetime(row['start_date']).date(),
                    'end_date': pd.to_datetime(row['end_date']).date(),
                }
            )

        self.stdout.write(self.style.SUCCESS("Data loaded successfully."))
