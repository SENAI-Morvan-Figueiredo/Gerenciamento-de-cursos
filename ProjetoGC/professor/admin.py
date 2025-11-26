from django.contrib import admin
from .models import Aula, Frequencia

admin.site.register(Aula)
admin.site.register(Frequencia)

class FrequenciaAdmin(admin.ModelAdmin):
    list_display = ('aula', 'matricula', 'presenca')
    search_fields = ('aula', 'matricula', 'presenca')

class AulaAdmin(admin.ModelAdmin):
    list_display = ('data', 'tipo', 'turma')
    search_fields = ('data', 'tipo', 'turma')
    # Register your models here.
