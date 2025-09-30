# aluno/urls.py
from django.urls import path
from .views import dashboard_professor

urlpatterns = [
    path('dashboard/', dashboard_professor, name='dashboard_professor'),
]