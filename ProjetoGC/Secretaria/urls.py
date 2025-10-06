from django.urls import path
from .views import (
    TurmaListView, TurmaCreateView, TurmaUpdateView,
    AlunoListView, AlunoCreateView, AlunoUpdateView, AlunoDetailView,
    ProfessorListView, ProfessorCreateView, ProfessorUpdateView, ProfessorDetailView,
)

app_name = 'secretaria'

urlpatterns = [
    path('turmas/', TurmaListView.as_view(), name='turmaList'),
    path('turmas/add/', TurmaCreateView.as_view(), name='turmaAdd'),
    path('turmas/<int:pk>/update/', TurmaUpdateView.as_view(), name='turmaUpdate'),
    # path('turmas/<int:pk>/detail/', TurmaDetailView.as_view(), name='turmaDetail'),

    path('alunos/', AlunoListView.as_view(), name='alunoList'),
    path('alunos/add/', AlunoCreateView.as_view(), name='alunoAdd'),
    path('alunos/<int:pk>/update/', AlunoUpdateView.as_view(), name='alunoUpdate'),
    # path('alunos/<int:pk>/detail/', AlunoDetailView.as_view(), name='alunoDetail'),

    path('professores/', ProfessorListView.as_view(), name='profList'),
    path('professores/add/', ProfessorCreateView.as_view(), name='profAdd'),
    path('professores/<int:pk>/update/', ProfessorUpdateView.as_view(), name='profUpdate'),
    # path('professores/<int:pk>/detail/', ProfessorDetailView.as_view(), name='profDetail'),

    
]