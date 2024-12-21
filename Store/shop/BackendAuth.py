from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from .models import Customer

class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user = Customer.objects.get(email = email)
            if user.check_password(password):
                return user
        except Customer.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Customer.objects.get(pk=user_id)
        except Customer.DoesNotExist:
            return None
