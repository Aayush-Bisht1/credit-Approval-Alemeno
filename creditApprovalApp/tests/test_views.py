from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from creditApprovalApp.models import Customer

class CustomerTests(APITestCase):

    def test_register_customer(self):
        url = reverse("register")  # Make sure the URL pattern has a name="register"
        data = {
            "first_name": "Test",
            "last_name": "User",
            "age": 30,
            "monthly_income": 50000,
            "phone_number": "1234567000"
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Customer.objects.filter(phone_number="1234567000").exists())
