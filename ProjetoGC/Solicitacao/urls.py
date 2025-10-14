from django.urls import path
from .views import SolicitacaoListView


app_name = 'solicitacao'

urlpatterns = [
    path('solicitacoes/', SolicitacaoListView.as_view(), name='solicitacaoList'),
]