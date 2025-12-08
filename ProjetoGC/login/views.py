from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.views import PasswordResetView
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomPasswordResetForm
import logging
import smtplib

User = get_user_model()

logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        print(f"Tentando autenticar: {email}")  # DEBUG
        
        user = authenticate(request, username=email, password=password)
        
        print(f"Usuário autenticado: {user}")  # DEBUG
        if user:
            print(f"Tipo do usuário: {getattr(user, 'tipo', 'CAMPO TIPO NÃO EXISTE')}")  # DEBUG
            print(f"Atributos do usuário: {dir(user)}")  # DEBUG
        
        if user is not None:
            login(request, user)
           
            
            # DEBUG: Verificar todos os atributos
            print("=== DEBUG USER ===")
            print(f"User: {user}")
            print(f"Tipo: {getattr(user, 'tipo', 'N/A')}")
            print(f"Email: {getattr(user, 'email', 'N/A')}")
            print(f"First name: {getattr(user, 'first_name', 'N/A')}")
            print("==================")
            
            # Redireciona conforme tipo
            if hasattr(user, 'tipo'):
                if user.tipo == "aluno":
                    return redirect('aluno:dashboard_aluno')
                elif user.tipo == "professor":
                    return redirect('professor:home')
                elif user.tipo == "secretaria":
                    return redirect('secretaria:turmaList')
            else:
                # Se não tem campo tipo, trata como admin ou redireciona para página padrão
                messages.warning(request, "Usuário sem tipo definido")
                return redirect("admin:index")  # ou outra página
            
        else:
            messages.error(request, "E-mail ou senha incorretos.")

    return render(request, "login/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")  # Redireciona para a página de login

from django.contrib import messages


def password_reset_done(request):
    messages.success(request, 'Um email com instruções foi enviado para você.')
    return render(request, 'login/password_reset_done.html')




class CustomPasswordResetView(PasswordResetView):
    template_name = 'login/password_reset_form.html'
    html_email_template_name = 'login/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
    form_class = CustomPasswordResetForm

    def post(self, request, *args, **kwargs):
        """
        Intercepta o POST para:
         - validar o form
         - verificar se existe usuário ativo com o e-mail
         - enviar e redirecionar se existir
         - mostrar erro se não existir
        """
        form = self.get_form()
        if not form.is_valid():
            # Form inválido (ex.: e-mail mal formatado) → reexibe com erros
            return self.form_invalid(form)

        email = form.cleaned_data.get('email', '').strip()
        # verifica existência de usuário ativo com esse e-mail
        user_qs = User.objects.filter(email__iexact=email, is_active=True)

        if not user_qs.exists():
            # NÃO encontrou usuário → mensagem de erro e reexibe o form
            messages.error(request, "E-mail não encontrado no sistema.")
            return self.form_invalid(form)

        # Se existe usuário ativo, tenta enviar o email e redirecionar
        try:
            # form_valid executa o envio padrão (form.save -> envia emails)
            response = super().form_valid(form)
        except Exception as e:
            # Log e mensagem amigável
            logger.exception("Erro ao enviar email de redefinição: %s", e)
            messages.error(request, "Erro ao enviar o e-mail. Tente novamente mais tarde.")
            return self.form_invalid(form)

        # Garantir redirecionamento para a página correta
        return redirect(self.success_url)

    def get_users(self, email):
        """Retorna queryset de usuários que receberão o e-mail (mantive sua lógica)."""
        return User.objects.filter(email__iexact=email, is_active=True)

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Método responsável por montar e enviar o email. Mantive seu comportamento,
        com tratamento de exceções e timeout.
        """
        subject = "Redefinição de senha - Sistema de Gerenciamento de Cursos"
        html_email = render_to_string(self.html_email_template_name, context)
        text_email = (
            f"Olá {context.get('user').get_username() if context.get('user') else ''},\n\n"
            "Você solicitou uma redefinição de senha.\n"
            f"Acesse o link abaixo:\n"
            f"{context['protocol']}://{context['domain']}/reset/{context['uid']}/{context['token']}/\n\n"
            "Se não foi você, ignore este e-mail."
        )

        try:
            connection = get_connection(
                backend='django.core.mail.backends.smtp.EmailBackend',
                fail_silently=False,
                timeout=30,
            )

            msg = EmailMultiAlternatives(
                subject, text_email, from_email, [to_email], connection=connection
            )
            msg.attach_alternative(html_email, "text/html")
            msg.send()
        except Exception as e:
            logger.exception("Falha ao enviar email de redefinição: %s", e)
            # Usamos messages para informar ao usuário (self.request existe no contexto da view)
            messages.error(self.request, "Erro ao enviar o e-mail. Tente novamente mais tarde.")
            # Re-raise se quiser interromper; aqui apenas logamos e deixamos o fluxo tratar.
            raise