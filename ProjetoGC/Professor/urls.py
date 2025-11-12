from django.urls import path, include
from . import views

app_name = 'professor'

# professor/urls.py
urlpatterns = [
    path('home/', views.home, name='home'),
    path('dashboard/turma/<int:turma_id>/', views.dashboard_turma_detalhes, name='dashboard_turma_detalhes'),

    # 👇 nova rota para o calendário
    path('calendario/', include('Calendario.urls', namespace='calendario_professor')),
]
