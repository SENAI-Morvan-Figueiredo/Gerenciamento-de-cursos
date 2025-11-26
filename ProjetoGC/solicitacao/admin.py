from django.contrib import admin
from .models import Solicitacao

admin.site.register(Solicitacao)

class SolicitacaoAdmin(admin.ModelAdmin):
    list_display = ('solicitacao_id', 'secretaria', 'usuario', 'tipo', 'data_solicitacao', 'status')
    search_fields = ('solicitacao_id', 'secretaria', 'usuario', 'tipo', 'data_solicitacao', 'status')