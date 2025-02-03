from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import Customer




# Authentication for Cutomer Model
class CustomerAuthenticationBackend(BaseBackend):
    """
    Custom authentication backend to handle login with Customer model.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user against the Customer model using email and password.
        """
        try:
            # Try to find the user by email
            customer = Customer.objects.get(email=username)
            
            # Check if the password is correct
            if check_password(password, customer.password):
                return customer  # Authentication successful
        except Customer.DoesNotExist:
            # No customer found with the provided email
            return None

    def get_user(self, user_id):
        """
        Retrieve a user instance based on the ID.
        """
        try:
            return Customer.objects.get(id=user_id)
        except Customer.DoesNotExist:
            return None
