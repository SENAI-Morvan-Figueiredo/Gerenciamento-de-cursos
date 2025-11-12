# Calendario/urls.py
from django.urls import path
from . import views

app_name = 'calendario'

urlpatterns = [
    path('professor/', views.calendario_professor, name='calendario_professor'),
    path('aluno/', views.calendario_aluno, name='calendario_aluno'),
    path('secretaria/', views.calendario_secretaria, name='calendario_secretaria'),

    # endpoint para o FullCalendar
    path('eventos/', views.listar_eventos, name='listar_eventos'),
]
