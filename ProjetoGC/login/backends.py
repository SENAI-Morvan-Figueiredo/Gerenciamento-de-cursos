# backends.py - SUBSTITUA TODO O CONTEÚDO por:
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

class EmailOnlyBackend(BaseBackend):
    """
    Backend APENAS para email - funciona com Password Reset
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        # IMPORTANTE: Django Password Reset envia 'email' no kwargs
        # Login normal envia 'username'
        email = username or kwargs.get('email')
        
        if not email:
            return None
            
        try:
            # Procura APENAS por email
            user = UserModel.objects.get(email=email)
            if user.check_password(password):
                return user
            return None
        except UserModel.DoesNotExist:
            # Para compatibilidade com usuários antigos
            try:
                user = UserModel.objects.get(username=email)
                if user.check_password(password):
                    return user
                return None
            except UserModel.DoesNotExist:
                return None
        except UserModel.MultipleObjectsReturned:
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