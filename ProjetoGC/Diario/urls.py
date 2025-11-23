# diario/urls.py
from django.urls import path
from . import views

app_name = 'diario'

urlpatterns = [
    path('', views.lista_turmas_diario, name='lista_turmas_diario'),
    path('turma/<int:turma_id>/nova-aula/', views.criar_aula, name='criar_aula'),
    path('aula/<int:aula_id>/chamada/', views.registrar_chamada, name='registrar_chamada'),
    path('aula/<int:aula_id>/salvar-chamada/', views.salvar_chamada, name='salvar_chamada'),
    path('turma/<int:turma_id>/historico/', views.historico_aulas, name='historico_aulas'),
    path('turma/<int:turma_id>/relatorio/', views.relatorio_frequencia, name='relatorio_frequencia'),
]