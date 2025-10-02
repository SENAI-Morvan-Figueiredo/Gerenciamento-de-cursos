from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from Cursos.models import Curso, Disciplina, Turma, Matricula, GradeCurricular
from Login.models import Usuario, Aluno, Professor, Secretaria
from Atividades.models import Atividade, AtividadeEntregue
from Professor.models import Aula, Frequencia
from Secretaria.models import Solicitacao

# Personalização para o modelo Usuario (se for custom User model)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'tipo_usuario')
    list_filter = ('tipo_usuario', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')

# Personalização para outros modelos
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'duracao', 'coordenador')
    list_filter = ('duracao',)
    search_fields = ('nome',)

class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'carga_horaria', 'curso')
    list_filter = ('curso',)
    search_fields = ('nome',)

class AlunoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'matricula', 'curso', 'data_ingresso')
    list_filter = ('curso', 'data_ingresso')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'matricula')

class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'departamento', 'formacao')
    list_filter = ('departamento',)
    search_fields = ('usuario__first_name', 'usuario__last_name')

class TurmaAdmin(admin.ModelAdmin):
    list_display = ('disciplina', 'professor', 'ano', 'semestre')
    list_filter = ('ano', 'semestre', 'disciplina__curso')
    search_fields = ('disciplina__nome', 'professor__usuario__first_name')

class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'turma', 'data_matricula', 'status')
    list_filter = ('status', 'turma__disciplina__curso')
    search_fields = ('aluno__usuario__first_name', 'aluno__usuario__last_name')

class AtividadeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'disciplina', 'data_entrega', 'valor')
    list_filter = ('disciplina', 'data_entrega')
    search_fields = ('titulo', 'disciplina__nome')

class AtividadeEntregueAdmin(admin.ModelAdmin):
    list_display = ('atividade', 'aluno', 'data_entrega', 'nota')
    list_filter = ('atividade__disciplina',)
    search_fields = ('aluno__usuario__first_name', 'atividade__titulo')

class AulaAdmin(admin.ModelAdmin):
    list_display = ('turma', 'data', 'conteudo')
    list_filter = ('turma', 'data')
    search_fields = ('conteudo', 'turma__disciplina__nome')

class FrequenciaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'aula', 'presenca')
    list_filter = ('presenca', 'aula__turma')
    search_fields = ('aluno__usuario__first_name',)

class SolicitacaoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'tipo', 'data_solicitacao', 'status')
    list_filter = ('tipo', 'status', 'data_solicitacao')
    search_fields = ('aluno__usuario__first_name', 'tipo')

# Registro dos modelos com as personalizações
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Curso, CursoAdmin)
admin.site.register(Disciplina, DisciplinaAdmin)
admin.site.register(Aluno, AlunoAdmin)
admin.site.register(Professor, ProfessorAdmin)
admin.site.register(Turma, TurmaAdmin)
admin.site.register(Matricula, MatriculaAdmin)
admin.site.register(Atividade, AtividadeAdmin)
admin.site.register(AtividadeEntregue, AtividadeEntregueAdmin)
admin.site.register(Aula, AulaAdmin)
admin.site.register(Frequencia, FrequenciaAdmin)
admin.site.register(Solicitacao, SolicitacaoAdmin)

# Modelos sem personalização específica (mantenha os básicos)
admin.site.register(Secretaria)
admin.site.register(GradeCurricular)