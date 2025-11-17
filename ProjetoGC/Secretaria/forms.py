from django import forms
from Login.models import Usuario, Aluno, Professor
from Cursos.models import Matricula, Turma, Curso
from django.db import transaction
from django.utils.text import slugify

class UsuarioBaseForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
                    'nome', 'sobrenome',
                    'cpf', 'data_nascimento',
                    'email', 'contato',
                    'endereco'
                ]
        labels = {
            'nome': 'Nome',
            'sobrenome': 'Sobrenome',
            'cpf': 'CPF',
            'data_nascimento': 'Data de Nascimento',
            'email': 'Email',
            'contato': 'Contato',
            'endereco': 'Endereço',
        }

    TIPO_USUARIO = [
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
        ('secretaria', 'Secretaria'),
    ]
        
    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get('nome')
        sobrenome = cleaned_data.get('sobrenome')
        
        if nome and sobrenome:
            base_username = slugify(f"{nome}.{sobrenome}")
            username = base_username
            counter = 1
            while Usuario.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            cleaned_data['username'] = username
        
        return cleaned_data
        
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)

        self.fields['nome'].widget.attrs.update({'class': 'form-control', 'required': True})
        self.fields['sobrenome'].widget.attrs.update({'class': 'form-control', 'required': True})

        self.fields['cpf'].widget.attrs.update({'class': 'form-control', 'required': True})
        self.fields['data_nascimento'].widget.attrs.update({'class': 'form-control', 'type': 'date', 'required': True})

        self.fields['email'].widget.attrs.update({'class': 'form-control', 'required': True})
        self.fields['contato'].widget.attrs.update({'class': 'form-control', 'required': True})

        self.fields['endereco'].widget.attrs.update({'class': 'form-control', 'required': True})
        
        is_creating = self.instance.pk is None
        
        if not is_creating:
            self.fields['tipo'] = forms.ChoiceField(
                choices=self.TIPO_USUARIO,
                widget=forms.Select(attrs={'class': 'form-control'}),
                label='Tipo de Usuário'
            )

class AlunoUsuarioForm(UsuarioBaseForm): 
    class Meta(UsuarioBaseForm.Meta):
        pass
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['turma'] = forms.ModelMultipleChoiceField(
            queryset=Turma.objects.all().exclude(status=False),
            required=False,
            widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input', 'data-select2': 'true'})
        )
        
        is_creating = self.instance.pk is None
        
        if is_creating:
            self.fields.pop('status_matricula', None)
        else:
            self.fields['status_matricula'] = forms.BooleanField(
                initial=True,
                label='Matriculado',
                widget=forms.CheckboxInput(attrs={'class': 'form-control'})
            )

        if self.instance and self.instance.pk:
            try:
                aluno = self.instance
                turmas_atuais = Turma.objects.filter(
                    matricula__aluno=aluno, 
                    matricula__status_matricula=True
                )
                
                tem_matriculas_ativas = Matricula.objects.filter(
                        aluno=aluno, 
                        status_matricula=True
                    ).exists()
                self.fields['status_matricula'].initial = tem_matriculas_ativas
                
                self.fields['turma'].initial = turmas_atuais
                self.fields['tipo'].initial = 'aluno'

                self.fields['nome'].initial = aluno.usuario.nome
                self.fields['email'].initial = aluno.usuario.email
                self.fields['cpf'].initial = aluno.usuario.cpf
                self.fields['sobrenome'].initial = aluno.usuario.sobrenome
                self.fields['contato'].initial = aluno.usuario.contato
                self.fields['endereco'].initial = aluno.usuario.endereco
                self.fields['data_nascimento'].initial = aluno.usuario.data_nascimento
                
            except Aluno.DoesNotExist:
                pass
    
    @transaction.atomic
    def save(self, commit=True):
        is_creating = self.instance.pk is None
        
        usuario = super().save(commit=False)
        
        if is_creating:
            usuario.tipo = 'aluno'
            usuario.status = True
            usuario.username = self.cleaned_data.get('username')
            usuario.set_password=self.cleaned_data["cpf"]

        if commit:
            usuario.save()
    
            if is_creating:
                aluno = Aluno.objects.create(usuario=usuario)
            else:
                aluno = usuario
            
            if not is_creating and 'status_matricula' in self.cleaned_data:
                status_matricula_geral = self.cleaned_data['status_matricula']
                
                if not status_matricula_geral:
                    Matricula.objects.filter(aluno=aluno).update(status_matricula=False)
                else:
                    matriculas_ativas = Matricula.objects.filter(
                        aluno=aluno, 
                        status_matricula=True
                    )
                    if not matriculas_ativas.exists():
                        turmas_selecionadas = self.cleaned_data.get('turma', [])
                        if turmas_selecionadas:
                            primeira_turma = turmas_selecionadas.first()
                            Matricula.objects.create(
                                aluno=aluno, 
                                turma=primeira_turma, 
                                status_matricula=True
                            )
            
            turmas_selecionadas = self.cleaned_data.get('turma', [])
            
            matriculas_atuais = Matricula.objects.filter(aluno=aluno)
            turmas_atuais = set(matricula.turma for matricula in matriculas_atuais)
            turmas_selecionadas_set = set(turmas_selecionadas)
            
            for matricula in matriculas_atuais:
                if matricula.turma not in turmas_selecionadas_set:
                    matricula.delete()
            
            for turma in turmas_selecionadas:
                if turma not in turmas_atuais:
                    Matricula.objects.create(
                        aluno=aluno, 
                        turma=turma, 
                        status_matricula=True
                    )
        
        return usuario

class ProfessorUsuarioForm(UsuarioBaseForm):
    class Meta(UsuarioBaseForm.Meta):
        pass
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

        self.fields['salario'] = forms.DecimalField(
            max_digits=10,
            decimal_places=2,
            required=True
        )

        is_creating = self.instance.pk is None

        if is_creating:
            self.fields.pop('status', None)
        else:
            self.fields['turma'] = forms.ModelMultipleChoiceField(
                queryset=Turma.objects.all().exclude(status=False),
                required=False,
                widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input', 'data-select2': 'true'}),
            )

            self.fields['status'] = forms.BooleanField(
                initial=True,
                widget=forms.CheckboxInput(attrs={'class': 'form-control', 'label': 'Ativo'})
            )


        if self.instance and self.instance.pk:
            try:
                professor = self.instance
                turmas_atuais = Turma.objects.filter(
                    professor=professor,
                    status=True
                )
                self.fields['turma'].initial = turmas_atuais
                self.fields['tipo'].initial = 'professor'
                
                self.fields['salario'].initial = professor.salario
                self.fields['status'].initial = professor.status

                self.fields['nome'].initial = professor.usuario.nome
                self.fields['email'].initial = professor.usuario.email
                self.fields['cpf'].initial = professor.usuario.cpf
                self.fields['sobrenome'].initial = professor.usuario.sobrenome
                self.fields['contato'].initial = professor.usuario.contato
                self.fields['endereco'].initial = professor.usuario.endereco
                self.fields['data_nascimento'].initial = professor.usuario.data_nascimento

            except Professor.DoesNotExist:
                pass

        self.fields['salario'].widget.attrs.update({'class': 'form-control', 'label': 'Salário'})

    @transaction.atomic
    def save(self, commit=True):
        is_creating = self.instance.pk is None

        usuario = super().save(commit=False)
        
        if is_creating:
            usuario.tipo = 'professor'
            usuario.username = self.cleaned_data.get('username')
            usuario.set_password(self.cleaned_data["cpf"])
            
        if commit:
            usuario.save()
            
            if is_creating:
                professor = Professor.objects.create(
                    usuario=usuario,
                    salario=self.cleaned_data['salario'],
                    status=True
                )
            else:
                professor = usuario.professor
                professor.salario = self.cleaned_data['salario']
                if 'status' in self.cleaned_data:
                    professor.status = self.cleaned_data['status']
                professor.save()
            
            if not is_creating:
                turmas_selecionadas = self.cleaned_data.get('turma', [])
                Turma.objects.filter(professor=professor).update(professor=None)
                for turma in turmas_selecionadas:
                    turma.professor = professor
                    turma.save()
        
        return usuario

class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = [
            "nome",
            "curso",
            "professor",
            "tipo",
            "entrada_horas",
            "saida_horas",
            "data_inicio",
            "data_fim",
            "dias_semana",
            "status"
        ]

        labels = {
            'entrada_horas': 'Horário de Entrada',
            'saida_horas': 'Horário de Saída',      
            'nome': 'Nome da Turma',
            'curso': 'Curso',
            'professor': 'Professor',
            'tipo': 'Tipo de Turma',
            'data_inicio': 'Data de Início',
            'data_fim': 'Data de Término',
            'status': 'Turma Ativa',
            'dias_semana': 'Dias da Semana'
        }

    DIA_SEMANA_CHOICES = [
        ('segunda', 'Segunda-feira'),
        ('terca', 'Terça-feira'),
        ('quarta', 'Quarta-feira'),
        ('quinta', 'Quinta-feira'),
        ('sexta', 'Sexta-feira'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo'),
    ]

    TIPO_CHOICES = [
        ('presencial', 'Presencial'),
        ('online', 'Online'),
        ('hibrido', 'Híbrido'),
    ]

    STATUS_CHOICES = [
        (True, 'Ativo'),
        (False, 'Inativo'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['curso'].queryset = Curso.objects.all()
        self.fields['professor'].queryset = Professor.objects.all()

        is_creating = self.instance.pk is None
        
        if is_creating:
            self.fields.pop('status', None)
        else:
            self.fields['status'] = forms.ChoiceField(
                choices=self.STATUS_CHOICES,
                initial=self.instance.status if self.instance else True,
                widget=forms.CheckboxInput(attrs={'class': 'form-control'})
            )

        self.fields['nome'].widget.attrs.update({
        'class': 'form-control', 
        'required': True, 
        'placeholder': 'Nome da Turma'
        })
        self.fields['curso'].widget.attrs.update({
            'class': 'form-control',
            'required': True
        })
        self.fields['professor'].widget.attrs.update({
            'class': 'form-control',
            'required': True
        })
        
        self.fields['tipo'] = forms.ChoiceField(
            choices=self.TIPO_CHOICES,
            widget=forms.Select(attrs={
                'class': 'form-control', 
                'required': True, 
                'placeholder': 'Selecione o tipo de turma'
            })
        )

        self.fields['entrada_horas'].widget = forms.TimeInput(attrs={
            'class': 'form-control', 
            'type': 'time', 
            'required': True
        })
        self.fields['saida_horas'].widget = forms.TimeInput(attrs={
            'class': 'form-control', 
            'type': 'time', 
            'required': True
        })

        self.fields['data_inicio'].widget = forms.DateInput(attrs={
            'class': 'form-control', 
            'type': 'date', 
            'required': True
        })
        self.fields['data_fim'].widget = forms.DateInput(attrs={
            'class': 'form-control', 
            'type': 'date', 
            'required': True
        })
        
        self.fields['dias_semana'] = forms.MultipleChoiceField(
            choices=self.DIA_SEMANA_CHOICES,
            required=True,
            widget=forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input', 
                'data-group': 'dias-semana', 
                'required': True
            })
        )

        if self.instance and self.instance.pk:
            if self.instance.dias_semana:
                dias_lista = self.instance.dias_semana.split(',')
                self.fields['dias_semana'].initial = [dia.strip() for dia in dias_lista]

    def clean_dias_semana(self):
        dias_semana = self.cleaned_data.get('dias_semana')
        if dias_semana:
            return ','.join(dias_semana)
        return ''

    def save(self, commit=True):
        turma = super().save(commit=False)
        
        if 'dias_semana' in self.cleaned_data:
            turma.dias_semana = self.cleaned_data['dias_semana']
        
        if commit:
            turma.save()
        
        return turma