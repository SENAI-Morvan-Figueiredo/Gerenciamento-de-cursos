# forms.py - APENAS o CustomPasswordResetForm modificado
from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Digite seu e-mail cadastrado'
        })
        self.fields['email'].label = "E-mail"

    # ✅ CORREÇÃO: Validação case-insensitive e com usuários ativos
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if not email:
            raise forms.ValidationError("Por favor, digite um e-mail.")
        
        # Normaliza o email
        email = email.strip()
        
        # Busca case-insensitive e apenas usuários ativos
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            # Mantenha a mesma mensagem de erro para não quebrar o frontend
            raise forms.ValidationError("E-mail inválido ou não cadastrado.")
        
        return email


# ✅ MANTENHA este formulário EXATAMENTE como está
class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ Traduzindo labels
        self.fields['new_password1'].label = "Nova senha"
        self.fields['new_password2'].label = "Confirmar nova senha"

        # ✅ Estilizando inputs
        self.fields['new_password1'].widget.attrs.update({
            "class": "input-field",
            "placeholder": "Digite a nova senha"
        })

        self.fields['new_password2'].widget.attrs.update({
            "class": "input-field",
            "placeholder": "Repita a nova senha"
        })

        # ✅ Mensagens de erro personalizadas
        self.fields['new_password1'].error_messages = {
            'required': 'Por favor, digite a nova senha.'
        }
        self.fields['new_password2'].error_messages = {
            'required': 'Por favor, confirme a nova senha.',
            'password_mismatch': 'As senhas não coincidem.'
        }