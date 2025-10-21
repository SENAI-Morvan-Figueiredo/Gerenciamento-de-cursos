from django.urls import path
from .views import SolicitacaoListView, SolicitacaoCreateView, SolicitacaoStatusView


app_name = 'solicitacao'

urlpatterns = [
    path('solicitacoes/', SolicitacaoListView.as_view(), name='solicitacaoList'),
    path('solicitacoes/add/', SolicitacaoCreateView.as_view(), name='solicitacaoAdd'),
    path('<int:pk>/<str:acao>/', SolicitacaoStatusView.as_view(), name='solicitacaoStatus'),
]