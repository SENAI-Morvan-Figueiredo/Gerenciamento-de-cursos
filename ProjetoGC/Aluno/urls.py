from django.urls import path, include
from .views import dashboard_aluno  

app_name = 'aluno'  

urlpatterns = [
    path('dashboard/', dashboard_aluno, name='dashboard_aluno'),
    path('calendario/', include('Calendario.urls', namespace='calendario_aluno')),
]