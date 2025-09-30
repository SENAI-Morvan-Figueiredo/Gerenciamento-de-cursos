# aluno/urls.py
from django.urls import path
from .views import dashboard_aluno

urlpatterns = [
    path('dashboard/', dashboard_aluno, name='dashboard_aluno'),
]