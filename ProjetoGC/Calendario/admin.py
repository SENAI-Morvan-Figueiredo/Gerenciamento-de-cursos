# Calendario/admin.py
from django.contrib import admin
from .models import Evento

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'turma', 'data_inicio', 'data_fim')
    search_fields = ('titulo', 'descricao')
    list_filter = ('turma', 'data_inicio', 'data_fim')
    readonly_fields = ()

    def save_model(self, request, obj, form, change):
        """Salva o evento normalmente (sem campo criado_por)."""
        super().save_model(request, obj, form, change)
