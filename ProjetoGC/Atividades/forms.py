from django import forms
from .models import Avaliacao
from django.forms.widgets import DateTimeInput

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['turma', 'titulo', 'descricao', 'data_limite_entrega', 'arquivo']
        widgets = {
            'data_limite_entrega': DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        professor = kwargs.pop('professor', None)
        super().__init__(*args, **kwargs)
        
        # Adicionar classes CSS do Bootstrap ou do template
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        # Filtrar o campo 'turma' para mostrar apenas as turmas do professor
        if professor:
            self.fields['turma'].queryset = professor.turma_set.all()
        else:
            # Se não houver professor, não deve haver turmas para selecionar
            self.fields['turma'].queryset = self.fields['turma'].queryset.none()
