from django.contrib import admin
from .models import Curso, Disciplina, Turma, Matricula, GradeCurricular


admin.site.register(Curso)
admin.site.register(Disciplina)
admin.site.register(Turma)
admin.site.register(Matricula)
admin.site.register(GradeCurricular)

class GradeCurricularAdmin(admin.ModelAdmin):
    list_display = ('curso', 'disciplina')
    search_fields = ('curso', 'disciplina')

class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'turma', 'data_ingresso', 'status_matricula')
    search_fields = ('aluno', 'turma', 'data_ingresso', 'status_matricula')

class TurmaAdmin(admin.ModelAdmin):
    list_display = ('turma_id', 'curso', 'professor', 'data_inicio', 'data_fim')
    search_fields = ('turma_id', 'curso', 'professor', 'data_inicio', 'data_fim')

class CursoAdmin(admin.ModelAdmin):
    list_display = ('curso_id', 'nome', 'descricao', 'duracao')
    search_fields = ('curso_id', 'nome', 'descricao', 'duracao')

class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ('disciplina_id', 'materia', 'descricao')
    search_fields = ('disciplina_id', 'materia', 'descricao')


# Register your models here.
