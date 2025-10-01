from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Usuario

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # autentica pelo email
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)  # <-- aqui só é chamado se user existe
            # redireciona conforme tipo
            if user.tipo == "aluno":
                return redirect('aluno:dashboard_aluno')
            elif user.tipo == "professor":
                return redirect('aluno:dashboard_professor')
            elif user.tipo == "secretaria":
                return redirect('secretaria:dashboard_secretaria')
            else:
                return redirect("home")
        else:
            messages.error(request, "E-mail ou senha incorretos.")

    # Se GET ou falha na autenticação
    return render(request, "login.html")
