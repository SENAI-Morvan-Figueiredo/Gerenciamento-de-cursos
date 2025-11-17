from django.urls import path, include
from .views import (
    TurmaListView, TurmaCreateView, TurmaUpdateView, TurmaDetailView,
    AlunoListView, AlunoCreateView, AlunoUpdateView, AlunoDetailView,
    ProfessorListView, ProfessorCreateView, ProfessorUpdateView, ProfessorDetailView,
    config_view
)
from Calendario import views as calendario_views

app_name = 'secretaria'

urlpatterns = [
    path('turmas/', TurmaListView.as_view(), name='turmaList'),
    path('turmas/add/', TurmaCreateView.as_view(), name='turmaAdd'),
    path('turmas/<int:pk>/update/', TurmaUpdateView.as_view(), name='turmaUpdate'),
    path('turmas/<int:pk>/detail/', TurmaDetailView.as_view(), name='turmaDetail'),

    path('alunos/', AlunoListView.as_view(), name='alunoList'),
    path('alunos/add/', AlunoCreateView.as_view(), name='alunoAdd'),
    path('alunos/<int:pk>/update/', AlunoUpdateView.as_view(), name='alunoUpdate'),
    path('alunos/<int:pk>/detail/', AlunoDetailView.as_view(), name='alunoDetail'),

    path('professores/', ProfessorListView.as_view(), name='profList'),
    path('professores/add/', ProfessorCreateView.as_view(), name='profAdd'),
    path('professores/<int:pk>/update/', ProfessorUpdateView.as_view(), name='profUpdate'),
    path('professores/<int:pk>/detail/', ProfessorDetailView.as_view(), name='profDetail'),
    # Top-level calendar page for secretaria: /secretaria/calendario/
    path('calendario/', calendario_views.calendario_secretaria, name='calendario'),

    # API endpoints (eventos/) mounted under the same prefix:
    # /secretaria/calendario/eventos/
    path('calendario/', include(('Calendario.urls', 'calendario'), namespace='calendario_secretaria_api')),

    path('config/', config_view, name='config'),
]