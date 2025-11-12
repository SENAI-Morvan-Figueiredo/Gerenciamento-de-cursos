from django.urls import path, include
from . import views

app_name = 'professor'  # importante para usar namespaced URLs

# professor/urls.py
urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('dashboard/turma/<int:turma_id>/', views.dashboard_turma_detalhes, name='dashboard_turma_detalhes'),
    path('calendario/', include('Calendario.urls', namespace='calendario_professor')),
]
