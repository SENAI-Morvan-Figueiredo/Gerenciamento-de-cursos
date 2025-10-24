from django import forms
from .models import Solicitacao
from Login.models import Aluno, Professor
from Cursos.models import Matricula, Turma  # ajuste o caminho do import conforme sua estrutura

class SolicitacaoForm(forms.ModelForm):

    class Meta:
        model = Solicitacao
        fields = ['tipo', 'justificativa']
        labels = {
            'tipo': 'Tipo de Solicitação',
            'justificativa': 'Justificativa (para trancamento)',
        }

    turma_origem = forms.ModelChoiceField(
        queryset=Turma.objects.none(),
        required=False,
        label="Turma de Origem"
    )

    turma_destino = forms.ModelChoiceField(
        queryset=Turma.objects.none(),
        required=False,
        label="Turma de Destino"
    )
#teste
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # 🔹 Carrega as turmas do usuário logo no GET
        if user:
            if user.tipo == 'aluno':
                try:
                    aluno = Aluno.objects.get(usuario=user)
                    # Turmas onde o aluno está matriculado e ativo
                    matriculas_ativas = Matricula.objects.filter(
                        aluno=aluno,
                        status_matricula=True
                    )
                    turmas_origem = Turma.objects.filter(
                        pk__in=matriculas_ativas.values_list('turma_id', flat=True),
                        status=True
                    )
                    self.fields['turma_origem'].queryset = turmas_origem

                    # 🔥 Carregar todas as turmas possíveis de destino (mesmo curso)
                    if turmas_origem.exists():
                        cursos_ids = turmas_origem.values_list('curso_id', flat=True).distinct()
                        turmas_destino = Turma.objects.filter(
                            curso_id__in=cursos_ids,
                            status=True
                        ).exclude(
                            pk__in=turmas_origem.values_list('pk', flat=True)
                        )
                        self.fields['turma_destino'].queryset = turmas_destino

                except Aluno.DoesNotExist:
                    self.fields['turma_origem'].queryset = Turma.objects.none()
                    self.fields['turma_destino'].queryset = Turma.objects.none()

            elif user.tipo == 'professor':
                try:
                    prof = Professor.objects.get(usuario=user)
                    turmas_origem = Turma.objects.filter(
                        professor=prof,
                        status=True
                    )
                    self.fields['turma_origem'].queryset = turmas_origem

                    if turmas_origem.exists():
                        cursos_ids = turmas_origem.values_list('curso_id', flat=True).distinct()
                        turmas_destino = Turma.objects.filter(
                            curso_id__in=cursos_ids,
                            status=True
                        ).exclude(
                            pk__in=turmas_origem.values_list('pk', flat=True)
                        )
                        self.fields['turma_destino'].queryset = turmas_destino

                except Professor.DoesNotExist:
                    self.fields['turma_origem'].queryset = Turma.objects.none()
                    self.fields['turma_destino'].queryset = Turma.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        turma_origem = cleaned_data.get('turma_origem')
        turma_destino = cleaned_data.get('turma_destino')

        # Validações para realocação
        if tipo == 'realocacao':
            if not turma_origem:
                raise forms.ValidationError("Selecione a turma de origem para realocação.")
            
            if not turma_destino:
                raise forms.ValidationError("Selecione a turma de destino para realocação.")
            
            if turma_origem == turma_destino:
                raise forms.ValidationError("A turma de destino deve ser diferente da turma de origem.")
            
            # 🔥 VALIDAÇÃO DE SEGURANÇA (mesmo curso)
            if turma_origem.curso != turma_destino.curso:
                raise forms.ValidationError(
                    "Erro de validação: A turma selecionada não é do mesmo curso."
                )

        return cleaned_data