from django.urls import path
from . import views

app_name = 'aluno'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard_aluno, name='dashboard_aluno'),
    
    # Turmas
    path('turmas/', views.minhas_turmas, name='minhas_turmas'),
    path('turma/<int:turma_id>/', views.detalhes_turma, name='detalhes_turma'),
    
    # Atividades
    path('atividades/', views.lista_atividades, name='lista_atividades'),
    path('atividade/<int:atividade_id>/entregar/', views.entregar_atividade, name='entregar_atividade'),
    
    # Calendário
    path('calendario/', views.calendario_aluno, name='calendario'),
    path('calendario/eventos/', views.eventos_aluno_api, name='eventos_api'),
    
    # Solicitações
    path('solicitacoes/', views.solicitacoes_aluno, name='solicitacoes'),
    
    # Perfil
    path('perfil/', views.perfil_aluno, name='perfil'),
]