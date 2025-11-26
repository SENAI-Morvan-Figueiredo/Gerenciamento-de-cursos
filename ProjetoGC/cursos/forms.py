from django import forms
from .models import Curso, Disciplina, GradeCurricular, Turma, Matricula
from Login.models import Professor, Aluno

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ["nome", "carga_horaria", "descricao", "disciplinas", "ativo"]
        labels = {
            'nome': 'Nome do Curso',
            'descricao': 'Descrição',
            'carga_horaria': 'Carga Horária (h)',
            'ativo': 'Curso Ativo',
            'disciplinas': 'Disciplinas'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configuração dos widgets com classes CSS
        self.fields['nome'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Nome do curso',
            'required': True
        })
        
        self.fields['descricao'].widget.attrs.update({
            'class': 'form-control', 
            'rows': 3, 
            'placeholder': 'Descrição do curso'
        })
        
        self.fields['carga_horaria'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Carga horária total',
            'min': 1,
            'required': True
        })
        
        is_creating = self.instance.pk is None
        
        if is_creating:
            self.fields.pop('ativo', None)
        else:
            self.fields['ativo'].widget.attrs.update({
                'class': 'form-check-input'
            })
        
        self.fields['disciplinas'].widget.attrs.update({
            'class': 'form-check-input',
            'data-select2': 'true'
        })
        
        # Estilização específica para o campo disciplinas
        self.fields['disciplinas'].widget = forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input',
            'data-group': 'disciplinas'
        })
        
        self.fields['disciplinas'].queryset = Disciplina.objects.all()
        
        # Se estiver editando, mostrar as disciplinas atuais selecionadas
        if self.instance and self.instance.pk:
            self.fields['disciplinas'].initial = self.instance.disciplinas.all()

class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ['nome', 'carga_horaria', 'descricao']
        labels = {
            'nome': 'Nome da Disciplina',
            'descricao': 'Descrição',
            'carga_horaria': 'Carga Horária (h)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['nome'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Nome da disciplina',
            'required': True
        })
        
        self.fields['descricao'].widget.attrs.update({
            'class': 'form-control', 
            'rows': 3, 
            'placeholder': 'Descrição da disciplina'
        })
        
        self.fields['carga_horaria'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Carga horária da disciplina',
            'min': 1,
            'required': True
        })
