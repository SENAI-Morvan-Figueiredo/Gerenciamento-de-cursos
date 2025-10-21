from django.contrib import admin
from .models import Atividade, AtividadeEntregue

@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ('atividade_id', 'turma', 'titulo', 'descricao', 'tipo_material', 'url_material', 'data_entrega')
    search_fields = ('atividade_id', 'turma', 'titulo', 'descricao', 'tipo_material', 'url_material', 'data_entrega')

@admin.register(AtividadeEntregue)
class AtividadeEntregueAdmin(admin.ModelAdmin):
    list_display = ('atividade_entregue_id', 'atividade', 'matricula', 'texto', 'tipo_arquivo', 'url_arquivo', 'data_entrega', 'nota')
    search_fields = ('atividade_entregue_id', 'atividade', 'matricula', 'texto', 'tipo_arquivo', 'url_arquivo', 'data_entrega', 'nota')

