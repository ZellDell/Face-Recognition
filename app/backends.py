from django.contrib.auth.backends import BaseBackend
from .models import Accounts
from django.contrib.auth.hashers import check_password, make_password

class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, Username=None, Password=None):
        try:
            user = Accounts.objects.get(Username=Username)
            if user and check_password(Password, user.Password):
                return user
        except Accounts.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            
            return Accounts.objects.get(pk=user_id)
        except Accounts.DoesNotExist:
            return None
