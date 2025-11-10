from django.contrib import admin
from .models import Curso, Disciplina, Turma, Matricula, GradeCurricular


@admin.register(GradeCurricular)
class GradeCurricularAdmin(admin.ModelAdmin):
    list_display = ('curso', 'disciplina')
    search_fields = ('curso', 'disciplina')

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'turma', 'data_ingresso', 'status_matricula')
    search_fields = ('aluno', 'turma', 'data_ingresso', 'status_matricula')

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('turma_id', 'curso', 'professor', 'data_inicio', )
    search_fields = ('turma_id', 'curso', 'professor', 'data_inicio',)

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'descricao') 
    search_fields = ('id', 'nome', 'descricao')

@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'descricao')
    search_fields = ('id', 'nome', 'descricao')
