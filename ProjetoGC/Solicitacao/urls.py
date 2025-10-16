from django.urls import path
from .views import SolicitacaoListView, SolicitacaoCreateView, update_stat_solicitacao


app_name = 'solicitacao'

urlpatterns = [
    path('solicitacoes/', SolicitacaoListView.as_view(), name='solicitacaoList'),
    path('solicitacoes/add/', SolicitacaoCreateView.as_view(), name='solicitacaoAdd'),
    path('solicitacoes/<int:pk>/<str:acao>/',update_stat_solicitacao, name='solicitacaoStatus'),
]