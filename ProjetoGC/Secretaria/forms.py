from django import forms
from Login.models import Usuario, Aluno, Professor
from Cursos.models import Matricula, Turma, Curso
from django.utils.text import slugify


class AlunoUsuarioForm(forms.ModelForm):
    # Campos do Usuario
    nome = forms.CharField(max_length=150, required=True)
    sobrenome = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    contato = forms.CharField(max_length=20, required=True)
    turma = forms.ModelChoiceField(
        queryset=Turma.objects.all(),
        required=True,
        empty_label="Selecione uma turma"
    )
    cpf = forms.CharField(max_length=14, required=True)
    endereco = forms.CharField(widget=forms.Textarea, required=True)
    data_nascimento = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), required=True)
    
    class Meta:
        model = Aluno
        fields = ["data_ingresso"]
        widgets = {
            "data_ingresso": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Preenche os campos do usuário se estiver editando
        if self.instance and self.instance.pk and hasattr(self.instance, 'usuario'):
            usuario = self.instance.usuario
            self.fields['nome'].initial = usuario.nome
            self.fields['sobrenome'].initial = usuario.sobrenome
            self.fields['email'].initial = usuario.email
            self.fields['contato'].initial = usuario.contato
            self.fields['cpf'].initial = usuario.cpf
            self.fields['endereco'].initial = usuario.endereco
            self.fields['data_nascimento'].initial = usuario.data_nascimento

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.instance and self.instance.pk and hasattr(self.instance, 'usuario'):
            if Usuario.objects.filter(email=email).exclude(pk=self.instance.usuario.pk).exists():
                raise forms.ValidationError("Já existe um usuário com este e-mail.")
        else:
            if Usuario.objects.filter(email=email).exists():
                raise forms.ValidationError("Já existe um usuário com este e-mail.")
        return email

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if self.instance and self.instance.pk and hasattr(self.instance, 'usuario'):
            if Usuario.objects.filter(cpf=cpf).exclude(pk=self.instance.usuario.pk).exists():
                raise forms.ValidationError("Já existe um usuário com este CPF.")
        else:
            if Usuario.objects.filter(cpf=cpf).exists():
                raise forms.ValidationError("Já existe um usuário com este CPF.")
        return cpf

    def save(self, commit=True):
        # Se for atualização
        if self.instance and self.instance.pk:
            aluno = super().save(commit=False)
            usuario = self.instance.usuario
            
            # Atualiza usuário existente
            usuario.nome = self.cleaned_data["nome"]
            usuario.sobrenome = self.cleaned_data["sobrenome"]
            usuario.email = self.cleaned_data["email"]
            usuario.contato = self.cleaned_data["contato"]
            usuario.cpf = self.cleaned_data["cpf"]
            usuario.endereco = self.cleaned_data["endereco"]
            usuario.data_nascimento = self.cleaned_data["data_nascimento"]
            
            if commit:
                usuario.save()
                aluno.turma = self.cleaned_data["turma"]
                aluno.save()
            
            return aluno
        else:
            # CRIAÇÃO - cria novo usuário e aluno
            base_username = slugify(self.cleaned_data["nome"])
            username = base_username
            count = 1
            while Usuario.objects.filter(username=username).exists():
                username = f"{base_username}{count}"
                count += 1

            # Cria o usuário
            usuario = Usuario.objects.create(
                username=username,
                nome=self.cleaned_data["nome"],
                sobrenome=self.cleaned_data["sobrenome"],
                email=self.cleaned_data["email"],
                contato=self.cleaned_data["contato"],
                cpf=self.cleaned_data["cpf"],
                endereco=self.cleaned_data["endereco"],
                data_nascimento=self.cleaned_data["data_nascimento"],
                tipo="aluno"
            )
            
            # Cria o aluno vinculado ao usuário
            aluno = Aluno.objects.create(
                usuario=usuario,
                data_ingresso=self.cleaned_data["data_ingresso"],
                turma=self.cleaned_data["turma"]
            )
            
            return aluno

class ProfessorUsuarioForm(forms.ModelForm):
    # Campos do Usuario
    nome = forms.CharField(max_length=150, required=True)
    sobrenome = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    contato = forms.CharField(max_length=20, required=True)
    turmas = forms.ModelMultipleChoiceField(
        queryset=Turma.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    cpf = forms.CharField(max_length=14, required=True)
    endereco = forms.CharField(widget=forms.Textarea, required=True)
    data_nascimento = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), required=True)

    class Meta:
        model = Professor
        fields = ["salario", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and hasattr(self.instance, 'usuario'):
            usuario = self.instance.usuario
            self.fields['nome'].initial = usuario.nome
            self.fields['sobrenome'].initial = usuario.sobrenome
            self.fields['email'].initial = usuario.email
            self.fields['contato'].initial = usuario.contato
            self.fields['cpf'].initial = usuario.cpf
            self.fields['endereco'].initial = usuario.endereco
            self.fields['data_nascimento'].initial = usuario.data_nascimento
            self.fields['turmas'].initial = Turma.objects.filter(professor=self.instance)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.instance and self.instance.pk and hasattr(self.instance, 'usuario'):
            if Usuario.objects.filter(email=email).exclude(pk=self.instance.usuario.pk).exists():
                raise forms.ValidationError("Já existe um usuário com este e-mail.")
        else:
            if Usuario.objects.filter(email=email).exists():
                raise forms.ValidationError("Já existe um usuário com este e-mail.")
        return email

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if self.instance and self.instance.pk and hasattr(self.instance, 'usuario'):
            if Usuario.objects.filter(cpf=cpf).exclude(pk=self.instance.usuario.pk).exists():
                raise forms.ValidationError("Já existe um usuário com este CPF.")
        else:
            if Usuario.objects.filter(cpf=cpf).exists():
                raise forms.ValidationError("Já existe um usuário com este CPF.")
        return cpf

    def save(self, commit=True):
        # Se for atualização
        if self.instance and self.instance.pk:
            professor = super().save(commit=False)
            usuario = self.instance.usuario
            
            # Atualiza usuário existente
            usuario.nome = self.cleaned_data["nome"]
            usuario.sobrenome = self.cleaned_data["sobrenome"]
            usuario.email = self.cleaned_data["email"]
            usuario.contato = self.cleaned_data["contato"]
            usuario.cpf = self.cleaned_data["cpf"]
            usuario.endereco = self.cleaned_data["endereco"]
            usuario.data_nascimento = self.cleaned_data["data_nascimento"]
            
            if commit:
                usuario.save()
                professor.save()

                # Atualizar turmas
                turmas_selecionadas = self.cleaned_data["turmas"]
                Turma.objects.filter(professor=professor).exclude(pk__in=turmas_selecionadas).update(professor=None)
                for turma in turmas_selecionadas:
                    turma.professor = professor
                    turma.save()
            
            return professor
        else:
            # CRIAÇÃO - cria novo usuário e professor
            base_username = slugify(self.cleaned_data["nome"])
            username = base_username
            count = 1
            while Usuario.objects.filter(username=username).exists():
                username = f"{base_username}{count}"
                count += 1

            # Cria o usuário
            usuario = Usuario.objects.create(
                username=username,
                nome=self.cleaned_data["nome"],
                sobrenome=self.cleaned_data["sobrenome"],
                email=self.cleaned_data["email"],
                contato=self.cleaned_data["contato"],
                cpf=self.cleaned_data["cpf"],
                endereco=self.cleaned_data["endereco"],
                data_nascimento=self.cleaned_data["data_nascimento"],
                tipo="professor"
            )
            
            # Cria o professor
            professor = Professor.objects.create(
                usuario=usuario,
                salario=self.cleaned_data["salario"],
                status=self.cleaned_data["status"]
            )

            # Associa turmas
            turmas_selecionadas = self.cleaned_data["turmas"]
            for turma in turmas_selecionadas:
                turma.professor = professor
                turma.save()
            
            return professor


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



class TurmaForm(forms.ModelForm):
    curso = forms.ModelChoiceField(queryset=Curso.objects.all(), required=True)
    professor = forms.ModelChoiceField(queryset=Professor.objects.all(), required=True)
    
    dias_semana = forms.MultipleChoiceField(
        choices=DIA_SEMANA_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Dias da Semana"
    )

    horario = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        required=True
    )

    data_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )

    duracao = forms.IntegerField(
        min_value=1,
        required=True,
        label="Duração (em horas)"
    )

    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        required=True
    )

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=True
    )

    class Meta:
        model = Turma
        fields = [
            "curso",
            "professor",
            "dias_semana",
            "horario",
            "data_inicio",
            "duracao",
            "tipo",
            "status",
        ]


