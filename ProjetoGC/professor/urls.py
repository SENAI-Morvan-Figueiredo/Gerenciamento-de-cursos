from django.urls import path, include
from . import views
from calendario import views as calendario_views

app_name = 'professor'  # importante para usar namespaced URLs

# professor/urls.py
urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    
    path('dashboard/turma/<int:turma_id>/', views.dashboard_turma_detalhes, name='dashboard_turma_detalhes'),
    path('turmas/', views.listar_cursos, name='listar_cursos'),
    path('turmas/curso/<int:curso_id>/', views.turmas_por_curso, name='turmas_por_curso'),
    path('turma/<int:turma_id>/atividades/', views.listar_atividades, name='listar_atividades'),
    path('turma/<int:turma_id>/atividades/<int:atividade_id>/', views.atividade_detalhe, name='atividade_detalhe'),
    path('turma/<int:turma_id>/alunos/', views.listar_alunos_turma, name='listar_alunos_turma'),
    # Adicione esta linha no urlpatterns
    path('turma/<int:turma_id>/boletim/', views.boletim_turma, name='boletim_turma'),
    
    # Top-level calendar page for professors: /professor/calendario/
    path('calendario/', calendario_views.calendario_professor, name='calendario'),
    # API endpoints (eventos/) mounted under the same prefix: /professor/calendario/eventos/
    path('calendario/', include(('calendario.urls', 'calendario'), namespace='calendario_professor')),

]
