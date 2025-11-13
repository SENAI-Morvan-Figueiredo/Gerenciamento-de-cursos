from django.urls import path, include
from . import views
from Calendario import views as calendario_views

app_name = 'professor'  # importante para usar namespaced URLs

# professor/urls.py
urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('dashboard/turma/<int:turma_id>/', views.dashboard_turma_detalhes, name='dashboard_turma_detalhes'),

    # Top-level calendar page for professors: /professor/calendario/
    path('calendario/', calendario_views.calendario_professor, name='calendario'),

    # API endpoints (eventos/) mounted under the same prefix: /professor/calendario/eventos/
    path('calendario/', include(('Calendario.urls', 'calendario'), namespace='calendario_professor')),
]
