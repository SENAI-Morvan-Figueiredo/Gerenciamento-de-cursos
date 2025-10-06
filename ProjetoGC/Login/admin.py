from django.contrib import admin
from .models import Usuario, Aluno, Professor, Secretaria   

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ( 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('aluno_id', 'usuario', 'data_ingresso')

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('professor_id', 'usuario')

@admin.register(Secretaria)
class SecretariaAdmin(admin.ModelAdmin):
    list_display = ('secretaria_id', 'usuario')