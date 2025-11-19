from django.urls import path
from . import views

app_name = 'atividades'

urlpatterns = [
    path('', views.home_atividades, name='home'),
    path('<str:tipo_atividade>/visualizar/', views.visualizar_atividades, name='visualizar'),
    path('<str:tipo_atividade>/editar/', views.editar_atividades, name='editar'),
    path('avaliacao/adicionar/', views.adicionar_avaliacao, name='adicionar_avaliacao'),
    path('avaliacao/editar/<int:avaliacao_id>/', views.editar_avaliacao, name='editar_avaliacao'),
    path('avaliacao/deletar/<int:avaliacao_id>/', views.deletar_avaliacao, name='deletar_avaliacao'),
    path('avaliacao/listar/', views.listar_avaliacoes, name='listar_avaliacoes'),
    # Atividades (professor)
    path('atividade/adicionar/', views.adicionar_atividade, name='adicionar_atividade'),
    path('atividade/listar/', views.listar_atividades, name='listar_atividades'),
    # Atividades (aluno)
    path('aluno/atividades/', views.listar_atividades_aluno, name='aluno_listar_atividades'),
    path('aluno/atividade/<int:atividade_id>/entregar/', views.entregar_atividade, name='entregar_atividade'),
]
