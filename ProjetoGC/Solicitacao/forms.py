from django import forms
from .models import Solicitacao

class SolicitacaoForm(forms.ModelForm):
    class Meta:
        model = Solicitacao
        fields = ['tipo', 'justificativa']
        labels = {
            'tipo': 'Tipo de Solicitação',
            'justificativa': 'Justificativa (para trancamento)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Esconde o campo de justificativa por padrão
        self.fields['justificativa'].widget = forms.HiddenInput()

        # Se for um POST com tipo trancamento, mostra o campo
        tipo = self.data.get('tipo') or self.initial.get('tipo')
        if tipo == 'trancamento':
            self.fields['justificativa'].widget = forms.Textarea()