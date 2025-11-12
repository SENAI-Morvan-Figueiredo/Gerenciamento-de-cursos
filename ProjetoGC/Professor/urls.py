from django.urls import path, include
from . import views

app_name = 'professor'  # importante para usar namespaced URLs

# professor/urls.py
urlpatterns = [
<<<<<<< HEAD
    path('', views.home, name='home'),
=======
    path('home/', views.home, name='home'),
    path('dashboard/turma/<int:turma_id>/', views.dashboard_turma_detalhes, name='dashboard_turma_detalhes'),

    # 👇 nova rota para o calendário
    path('calendario/', include('Calendario.urls', namespace='calendario_professor')),
>>>>>>> d8b39aaae428546ed20ee50e0f4df44ef79e50e5
]
