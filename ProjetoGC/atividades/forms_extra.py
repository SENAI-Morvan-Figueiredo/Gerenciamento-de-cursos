from django import forms
from .models import Atividade, AtividadeEntregue
from Cursos.models import Turma


class AtividadeForm(forms.ModelForm):
    class Meta:
        model = Atividade
        fields = ['tipo', 'titulo', 'descricao', 'data_entrega', 'url_material', 'arquivo']
    
    def __init__(self, *args, **kwargs):
        professor = kwargs.pop('professor', None)
        super().__init__(*args, **kwargs)
        
        # Campo data_entrega como datetime-local
        self.fields['data_entrega'].widget = forms.DateTimeInput(
            attrs={'type': 'datetime-local'}
        )

        # Estilização
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})



class EntregaForm(forms.ModelForm):
    class Meta:
        model = AtividadeEntregue
        fields = ['texto', 'url_arquivo', 'tipo_arquivo']

    arquivo_upload = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
