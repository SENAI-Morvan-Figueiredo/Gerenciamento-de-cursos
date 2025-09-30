# aluno/urls.py
from django.urls import path
from .views import dashboard_secretaria

urlpatterns = [
    path('dashboard/', dashboard_secretaria, name='dashboard_secretaria'),
]