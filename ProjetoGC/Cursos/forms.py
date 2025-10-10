from django import forms
from .models import Curso, Disciplina, GradeCurricular, Turma, Matricula
from Login.models import Professor, Aluno


class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ["nome", "descricao", "carga_horaria", "ativo", "disciplinas"]
        widgets = {
            "disciplinas": forms.CheckboxSelectMultiple,
        }

class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ['nome', 'descricao', 'carga_horaria']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da disciplina'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição da disciplina'}),
        }