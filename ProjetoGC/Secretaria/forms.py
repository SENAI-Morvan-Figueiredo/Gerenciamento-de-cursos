from django import forms
from Login.models import Usuario, Aluno, Professor
from Cursos.models import Matricula, Turma, Curso
    
from django.utils.text import slugify

class UsuarioBaseForm(forms.ModelForm):
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmação de Senha', widget=forms.PasswordInput)
    
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
    
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)

        self.fields['nome'].widget.attrs.update({'class': 'form-control', 'required': True})
        self.fields['sobrenome'].widget.attrs.update({'class': 'form-control', 'required': True})

        self.fields['cpf'].widget.attrs.update({'class': 'form-control', 'required': True})
        self.fields['data_nascimento'].widget.attrs.update({'class': 'form-control', 'type': 'date', 'required': True})

        self.fields['email'].widget.attrs.update({'class': 'form-control', 'required': True})
        self.fields['contato'].widget.attrs.update({'class': 'form-control', 'required': True})

        self.fields['endereco'].widget.attrs.update({'class': 'form-control', 'required': True})
        
        # 🔹 Verifica se é uma criação (instance não existe ou não tem pk)
        is_creating = self.instance.pk is None
        
        # 🔹 Se for criação, remove o campo tipo
        # 🔹 Verifica se é uma criação (instance não existe ou não tem pk)
        is_creating = self.instance.pk is None
        
        # 🔹 Se for EDIÇÃO, adiciona o campo tipo
        if not is_creating:
            self.fields['tipo'] = forms.ChoiceField(
                choices=self.TIPO_USUARIO,
                widget=forms.Select(attrs={'class': 'form-control'}),
                label='Tipo de Usuário'
            )
        

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não coincidem")
        return password2
    


class AlunoUsuarioForm(UsuarioBaseForm): 
    class Meta(UsuarioBaseForm.Meta):
        pass
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔹 Campos do tipo ModelChoiceField, NÃO MECHA!
        # cria o Input do 'turma'
        self.fields['turma'] = forms.ModelMultipleChoiceField(
            queryset=Turma.objects.all().exclude(status=False),
            required=False,
            widget=forms.SelectMultiple(attrs={'class': 'form-control'})
        )
        
        is_creating = self.instance.pk is None
        
        # 🔹 Se for criação, remove o campo status_matricula
        if is_creating:
            self.fields.pop('status_matricula', None)
        else:
            # 🔹 Se for edição, mantém o campo status_matricula
            self.fields['status_matricula'] = forms.BooleanField(
                initial=True,
                label='Matriculado',
                widget=forms.CheckboxInput(attrs={'class': 'form-control'})
            )

        # Se for uma instância existente (edição)
        if self.instance and self.instance.pk:
            # Remove a obrigatoriedade da senha na edição
            self.fields['password1'].required = False
            self.fields['password2'].required = False
            
            # Preenche o campo turma com a turma atual do aluno
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


    
    def clean_password2(self):
        # Na edição, se senha não for fornecida, não valida
        if self.instance and self.instance.pk:
            password1 = self.cleaned_data.get("password1")
            password2 = self.cleaned_data.get("password2")
            if not password1 and not password2:
                return password2  # Permite edição sem alterar senha
        return super().clean_password2()
    
    def save(self, commit=True):

        is_creating = self.instance.pk is None
        
        usuario = super().save(commit=False)
        
        if is_creating:
            usuario.tipo = 'aluno'
            usuario.status = True

         # Só define nova senha se foi fornecida
        if self.cleaned_data.get("password1"):
            usuario.set_password(self.cleaned_data["password1"])
        
        if commit:
            usuario.save()
    
            # Cria o aluno
            if is_creating:
                aluno = Aluno.objects.create(usuario=usuario)
            else:
                aluno = usuario.aluno
            
            # 🔹 GERENCIAMENTO DO STATUS_MATRICULA (APENAS NA EDIÇÃO)
            if not is_creating and 'status_matricula' in self.cleaned_data:
                status_matricula_geral = self.cleaned_data['status_matricula']
                
                # Se desmarcou o status_matricula, desativa TODAS as matrículas
                if not status_matricula_geral:
                    Matricula.objects.filter(aluno=aluno).update(status_matricula=False)
                else:
                    # Se marcou como ativa, garante que pelo menos uma matrícula esteja ativa
                    matriculas_ativas = Matricula.objects.filter(
                        aluno=aluno, 
                        status_matricula=True
                    )
                    if not matriculas_ativas.exists():
                        # Se não há matrículas ativas, ativa a primeira turma selecionada
                        turmas_selecionadas = self.cleaned_data.get('turma', [])
                        if turmas_selecionadas:
                            primeira_turma = turmas_selecionadas.first()
                            Matricula.objects.create(
                                aluno=aluno, 
                                turma=primeira_turma, 
                                status_matricula=True
                            )
            
            # Gerencia as matrículas nas turmas específicas
            turmas_selecionadas = self.cleaned_data.get('turma', [])
            
            # Remove matrículas que não estão mais selecionadas
            matriculas_atuais = Matricula.objects.filter(aluno=aluno)
            turmas_atuais = set(matricula.turma for matricula in matriculas_atuais)
            turmas_selecionadas_set = set(turmas_selecionadas)
            
            # Desmatricula das turmas removidas
            for matricula in matriculas_atuais:
                if matricula.turma not in turmas_selecionadas_set:
                    matricula.delete()  # 🔹 Remove completamente a matrícula
            
            # Matricula nas novas turmas
            for turma in turmas_selecionadas:
                if turma not in turmas_atuais:
                    Matricula.objects.create(
                        aluno=aluno, 
                        turma=turma, 
                        status_matricula=True
                    )
        
        return usuario
    
    class MatriculaForm(forms.ModelForm):
        class Meta:
            model = Matricula
            fields = [  
                        'aluno', 'turma',
                        'status_matricula'
                    ]


#  <------------------------- Professores ------------------------->

class ProfessorUsuarioForm(UsuarioBaseForm):
    class Meta(UsuarioBaseForm.Meta):
        pass
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

       # 🔹 Campos do tipo ModelChoiceField, NÃO MECHA!
        # cria o Input do 'turma'
        self.fields['turma'] = forms.ModelMultipleChoiceField(
            queryset=Turma.objects.all().exclude(status=False),
            required=False,

        )

        self.fields['salario'] = forms.DecimalField(
            max_digits=10,
            decimal_places=2,
            required=True
        )
        
        is_creating = self.instance.pk is None
        
        # 🔹 Se for criação, remove o campo status
        if is_creating:
            self.fields.pop('status', None)
        else:
            # 🔹 Se for edição, mantém o campo status
            self.fields['status'] = forms.BooleanField(
                initial=True,
                widget=forms.CheckboxInput(attrs={'class': 'form-control', 'label': 'Ativo'})
                
            )
            

        

        # Se for uma instância existente (edição)
        if self.instance and self.instance.pk:
            # Remove a obrigatoriedade da senha na edição
            self.fields['password1'].required = False
            self.fields['password2'].required = False
            
            # Preenche os campo com o professor atual
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

        
        # 🔹 Campos simples configurados diretamente, Colocações das class, id, labels e outros...
        self.fields['turma'].widget.attrs.update({'class': 'form-control', 'label': 'Turmas'})
        self.fields['salario'].widget.attrs.update({'class': 'form-control', 'label': 'Salário'})
        

    def clean_password2(self):
        # Na edição, se senha não for fornecida, não valida
        if self.instance and self.instance.pk:
            password1 = self.cleaned_data.get("password1")
            password2 = self.cleaned_data.get("password2")
            if not password1 and not password2:
                return password2  # Permite edição sem alterar senha
        return super().clean_password2()
    
    def save(self, commit=True):
        is_creating = self.instance is None

        usuario = super().save(commit=False)
        
        if is_creating:
            usuario.tipo = 'professor'
            
        if self.cleaned_data.get("password1"):
            usuario.set_password(self.cleaned_data["password1"])
        
        if commit:
            usuario.save()
            
            if is_creating:
                professor = Professor.objects.create(
                    usuario=usuario,
                    salario=self.cleaned_data['salario'],
                    status=True
                )
            else:
                professor = usuario
                professor.salario = self.cleaned_data['salario']
                if 'status' in self.cleaned_data:
                    professor.status = self.cleaned_data['status']
                professor.save()
            
            # Gerencia turmas
            turmas_selecionadas = self.cleaned_data.get('turma', [])
            Turma.objects.filter(professor=professor)
            for turma in turmas_selecionadas:
                turma.professor = professor
                turma.save()
        
        return usuario

        


# <----------------------- TURMA ------------------------>

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
        # feito para facil modificação dos campos de forma manual,
        # posteriormente mudar para algo mais automatizado.

        # 🔹 Campos do tipo ModelChoiceField, NÃO MECHA!
        self.fields['curso'].queryset = Curso.objects.all()
        self.fields['professor'].queryset = Professor.objects.all()

        # 🔹 Verifica se é uma criação (instance não existe ou não tem pk)
        is_creating = self.instance.pk is None
        
        # 🔹 Se for criação, remove o campo status
        if is_creating:
            self.fields.pop('status', None)
        else:
            # 🔹 Se for edição, mantém o campo status
            self.fields['status'] = forms.ChoiceField(
                choices=self.STATUS_CHOICES,
                initial=self.instance.status if self.instance else True,
                widget=forms.CheckboxInput(attrs={'class': 'form-control'})
            )

        # 🔹 Campos simples configurados diretamente, Colocações das class, id, labels e outros...
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
        
        # 🔹 Campo tipo
        self.fields['tipo'] = forms.ChoiceField(
            choices=self.TIPO_CHOICES,
            widget=forms.Select(attrs={
                'class': 'form-control', 
                'required': True, 
                'placeholder': 'Selecione o tipo de turma'
            })
        )

        # 🔹 CORREÇÃO: Campos de hora - configurar o widget, não substituir o campo
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

        # 🔹 Campos de data
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
        
        # 🔹 Dias da semana
        self.fields['dias_semana'] = forms.MultipleChoiceField(
            choices=self.DIA_SEMANA_CHOICES,
            required=True,
            widget=forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input', 
                'data-group': 'dias-semana', 
                'required': True
            })
        )

        
        # Se estiver editando, preencher os valores iniciais para dias_semana
        if self.instance and self.instance.pk:
            # Converter a string de dias_semana para lista
            if self.instance.dias_semana:
                dias_lista = self.instance.dias_semana.split(',')
                self.fields['dias_semana'].initial = [dia.strip() for dia in dias_lista]

    def clean_dias_semana(self):
        dias_semana = self.cleaned_data.get('dias_semana')
        if dias_semana:
            # Converter lista para string separada por vírgulas
            return ','.join(dias_semana)
        return ''

    def save(self, commit=True):
        turma = super().save(commit=False)
        
        # Garantir que dias_semana seja salvo como string
        if 'dias_semana' in self.cleaned_data:
            turma.dias_semana = self.cleaned_data['dias_semana']
        
        if commit:
            turma.save()
        
        return turma