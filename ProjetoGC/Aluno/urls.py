from django.urls import path, include
from .views import dashboard_aluno  
from Calendario import views as calendario_views

app_name = 'aluno'  

urlpatterns = [
    path('dashboard/', dashboard_aluno, name='dashboard_aluno'),

    # Top-level calendar page for aluno: /aluno/calendario/
    path('calendario/', calendario_views.calendario_aluno, name='calendario'),

    # API endpoints mounted under same prefix: /aluno/calendario/eventos/
    path('calendario/', include(('Calendario.urls', 'calendario'), namespace='calendario_aluno_api')),
]