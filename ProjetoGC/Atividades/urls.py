from django.urls import path
from . import views

app_name = 'atividades'

urlpatterns = [
    path('', views.home_atividades, name='home'),
    path('<str:tipo_atividade>/visualizar/', views.visualizar_atividades, name='visualizar'),
    path('<str:tipo_atividade>/editar/', views.editar_atividades, name='editar'),
    path('avaliacao/adicionar/', views.adicionar_avaliacao, name='adicionar_avaliacao'),
    path('avaliacao/listar/', views.listar_avaliacoes, name='listar_avaliacoes'),
]
