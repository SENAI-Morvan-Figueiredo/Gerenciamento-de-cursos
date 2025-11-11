from django.contrib import admin
from .models import Evento


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'turma', 'data_inicio', 'data_fim', 'criado_por')
    list_filter = ('turma', 'data_inicio')
    search_fields = ('titulo', 'descricao', 'turma__nome', 'criado_por__username')
    ordering = ('data_inicio',)
    date_hierarchy = 'data_inicio'
    readonly_fields = ('criado_por',)

    def save_model(self, request, obj, form, change):
        """Define automaticamente o criador do evento."""
        if not obj.criado_por_id:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)
