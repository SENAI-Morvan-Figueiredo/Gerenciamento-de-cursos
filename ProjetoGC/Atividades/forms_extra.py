from django import forms
from .models import Atividade, AtividadeEntregue
from Cursos.models import Turma


class AtividadeForm(forms.ModelForm):
    class Meta:
        model = Atividade
        fields = ['turma', 'tipo', 'titulo', 'descricao', 'tipo_material', 'arquivo', 'url_material', 'data_entrega']

    def __init__(self, *args, **kwargs):
        professor = kwargs.pop('professor', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        # Filtrar turmas pelo professor quando fornecido
        if professor is not None:
            self.fields['turma'].queryset = Turma.objects.filter(professor=professor)
        else:
            self.fields['turma'].queryset = Turma.objects.none()


class EntregaForm(forms.ModelForm):
    class Meta:
        model = AtividadeEntregue
        fields = ['texto', 'url_arquivo', 'tipo_arquivo']

    arquivo_upload = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
