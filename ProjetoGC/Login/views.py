from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

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
            messages.success(request, f"Bem-vindo(a), {user.nome}!")
            
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

    return render(request, "login.html")