from django.urls import path
from .views import dashboard_aluno  

app_name = 'aluno'  

urlpatterns = [
    path('dashboard/', dashboard_aluno, name='dashboard_aluno'),
]