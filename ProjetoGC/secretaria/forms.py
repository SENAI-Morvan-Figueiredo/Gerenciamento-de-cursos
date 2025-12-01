from django import forms
from login.models import Usuario, Aluno, Professor
from cursos.models import Matricula, Turma, Curso
from django.db import transaction
from django.utils.text import slugify
from .widgets import DataNascimentoWidget
from datetime import datetime
from django.core.exceptions import ValidationError

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
    
    def clean_data_nascimento(self):
        """Valida e converte a data de nascimento"""
        data_nascimento = self.cleaned_data.get('data_nascimento')
        
        if not data_nascimento:
            return data_nascimento
        
        # Se já for um objeto date, retorna
        if hasattr(data_nascimento, 'year'):
            return data_nascimento
        
        # Se for string, tenta converter
        if isinstance(data_nascimento, str):
            try:
                # Tenta formato YYYY-MM-DD
                return datetime.strptime(data_nascimento, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError('Data de nascimento inválida. Use o formato DD/MM/YYYY.')
        
        return data_nascimento
        
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
        self.fields['data_nascimento'].widget = DataNascimentoWidget(attrs={'class': 'form-control', 'required': True})

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
                # CORREÇÃO: Buscar o objeto Aluno relacionado ao Usuario
                aluno = Aluno.objects.get(usuario=self.instance)
                turmas_atuais = Turma.objects.filter(
                    matricula__aluno=aluno, 
                    matricula__status_matricula=True
                )
                
                tem_matriculas_ativas = Matricula.objects.filter(
                    aluno=aluno, 
                    status_matricula=True
                ).exists()
                
                if not is_creating:
                    self.fields['status_matricula'].initial = tem_matriculas_ativas
                
                self.fields['turma'].initial = turmas_atuais
                self.fields['tipo'].initial = 'aluno'

                # CORREÇÃO: Usar self.instance (Usuario) diretamente
                self.fields['nome'].initial = self.instance.nome
                self.fields['email'].initial = self.instance.email
                self.fields['cpf'].initial = self.instance.cpf
                self.fields['sobrenome'].initial = self.instance.sobrenome
                self.fields['contato'].initial = self.instance.contato
                self.fields['endereco'].initial = self.instance.endereco
                self.fields['data_nascimento'].initial = self.instance.data_nascimento
                
            except Aluno.DoesNotExist:
                # Se não existe aluno relacionado, é uma criação
                pass
    
    @transaction.atomic
    def save(self, commit=True):
        is_creating = self.instance.pk is None
        
        usuario = super().save(commit=False)
        
        if is_creating:
            usuario.tipo = 'aluno'
            usuario.status = True
            usuario.username = self.cleaned_data.get('username')
            usuario.set_password(self.cleaned_data["cpf"])

        if commit:
            usuario.save()
    
            if is_creating:
                aluno = Aluno.objects.create(usuario=usuario)
            else:
                # CORREÇÃO: Buscar o aluno existente
                aluno = Aluno.objects.get(usuario=usuario)
            
            # CORREÇÃO: Lógica simplificada para status_matricula
            if not is_creating and 'status_matricula' in self.cleaned_data:
                status_matricula_geral = self.cleaned_data['status_matricula']
                
                if not status_matricula_geral:
                    # Desativa todas as matrículas
                    Matricula.objects.filter(aluno=aluno).update(status_matricula=False)
                else:
                    # Ativa pelo menos uma matrícula se não houver nenhuma ativa
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
            
            # CORREÇÃO: Lógica simplificada para atualização de turmas
            turmas_selecionadas = self.cleaned_data.get('turma', [])
            
            # Remove matrículas de turmas não selecionadas
            Matricula.objects.filter(aluno=aluno).exclude(turma__in=turmas_selecionadas).delete()
            
            # Adiciona matrículas para turmas selecionadas que não existem
            for turma in turmas_selecionadas:
                Matricula.objects.get_or_create(
                    aluno=aluno, 
                    turma=turma,
                    defaults={'status_matricula': True}
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
                
                professor = Professor.objects.get(usuario=self.instance)
                turmas_atuais = Turma.objects.filter(
                    professor=professor,
                    status=True
                )
                self.fields['turma'].initial = turmas_atuais
                self.fields['tipo'].initial = 'professor'
                
                self.fields['salario'].initial = professor.salario
                self.fields['status'].initial = professor.status

                
                self.fields['nome'].initial = self.instance.nome
                self.fields['email'].initial = self.instance.email
                self.fields['cpf'].initial = self.instance.cpf
                self.fields['sobrenome'].initial = self.instance.sobrenome
                self.fields['contato'].initial = self.instance.contato
                self.fields['endereco'].initial = self.instance.endereco
                self.fields['data_nascimento'].initial = self.instance.data_nascimento

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
                professor = Professor.objects.get(usuario=usuario)
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

    dias_semana = forms.MultipleChoiceField(
        choices=DIA_SEMANA_CHOICES,
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input',
            'required': True
        }),
        label='Dias da Semana'
    )

    class Meta:
        model = Turma
        fields = [
            "nome", "curso", "professor", "tipo",
            "entrada_horas", "saida_horas", "data_inicio",
            "data_fim", "dias_semana", "status"
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
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar querysets
        self.fields['curso'].queryset = Curso.objects.all()
        self.fields['professor'].queryset = Professor.objects.all()
        
        # Configurar campo tipo
        self.fields['tipo'] = forms.ChoiceField(
            choices=self.TIPO_CHOICES,
            widget=forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            label='Tipo de Turma'
        )
        
        # Configurar status apenas para edição
        is_creating = self.instance.pk is None
        
        if is_creating:
            # Remover status na criação
            self.fields.pop('status', None)
        else:
            # Configurar status como checkbox na edição
            self.fields['status'] = forms.BooleanField(
                required=False,
                initial=self.instance.status if self.instance else True,
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                label='Turma Ativa'
            )
        
        # Configurar atributos dos campos
        campos_atributos = {
            'nome': {'class': 'form-control', 'placeholder': 'Nome da Turma'},
            'curso': {'class': 'form-control'},
            'professor': {'class': 'form-control'},
            'entrada_horas': {'class': 'form-control', 'type': 'time'},
            'saida_horas': {'class': 'form-control', 'type': 'time'},
            'data_inicio': {'class': 'form-control', 'type': 'date'},
            'data_fim': {'class': 'form-control', 'type': 'date'},
        }
        
        for campo, attrs in campos_atributos.items():
            if campo in self.fields:
                self.fields[campo].widget.attrs.update(attrs)
        
        # CONFIGURAÇÃO CRÍTICA: Preencher dias_semana quando está editando
        if self.instance and self.instance.pk and self.instance.dias_semana:
            # Converter string do banco para lista
            dias_salvos = self.instance.dias_semana
            # Remover espaços em branco e converter para lista
            if dias_salvos:
                dias_lista = [dia.strip() for dia in dias_salvos.split(',')]
                # Definir o valor inicial do campo
                self.fields['dias_semana'].initial = dias_lista
                print(f"DEBUG - Dias salvos no banco: {dias_salvos}")
                print(f"DEBUG - Dias convertidos para lista: {dias_lista}")

    def clean_dias_semana(self):
        dias_semana = self.cleaned_data.get('dias_semana')
        if dias_semana:
            # Converter lista para string separada por vírgula
            return ','.join(dias_semana)
        raise forms.ValidationError("Selecione pelo menos um dia da semana.")

    def clean(self):
        cleaned_data = super().clean()
        entrada = cleaned_data.get('entrada_horas')
        saida = cleaned_data.get('saida_horas')
        
        if entrada and saida and entrada >= saida:
            raise forms.ValidationError(
                "O horário de entrada deve ser anterior ao horário de saída."
            )
        
        return cleaned_data
    
    def get_dias_semana_list(self):
        """Retorna os dias da semana como lista"""
        if self.dias_semana:
            return [dia.strip() for dia in self.dias_semana.split(',')]
        return []
    
    def save(self, commit=True):
        turma = super().save(commit=False)
        
        if 'dias_semana' in self.cleaned_data:
            turma.dias_semana = self.cleaned_data['dias_semana']
        
        if commit:
            turma.save()
        
        return turma