from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

class EmailAuthBackend(BaseBackend):
    """
    Backend de autenticação que usa APENAS email
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        # Usa o email passado como 'username' no authenticate
        email = username
        
        try:
            user = UserModel.objects.get(email=email)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            # Se houver emails duplicados (o que não deveria acontecer com unique=True)
            users = UserModel.objects.filter(email=email)
            for user in users:
                if user.check_password(password):
                    return user
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None