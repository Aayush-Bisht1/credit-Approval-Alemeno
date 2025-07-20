from django.urls import path
from .views import *

urlpatterns = [
    path('register', RegisterCustomer.as_view()),
    path('register', RegisterCustomer.as_view(), name='register'),
    path('check-eligibility', CheckEligibility.as_view()),
    path('create-loan', CreateLoan.as_view()),
    path('view-loan/<int:loan_id>', ViewLoan.as_view()),
    path('view-loans/<int:customer_id>', ViewLoans.as_view()),
]
