# Aluno/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from Login.decorators import aluno_required

@login_required
@aluno_required
def dashboard_aluno(request):
    return render(request, "aluno/dashboard.html")
