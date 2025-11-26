from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.apps import apps
from .widgets import DataNascimentoWidget
from datetime import datetime

Usuario = get_user_model()

class UsuarioBaseForm(forms.ModelForm):
    TIPO_USUARIO = [
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
        ('secretaria', 'Secretaria'),
    ]

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

    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data.get('data_nascimento')
        if not data_nascimento:
            return data_nascimento
        if hasattr(data_nascimento, 'year'):
            return data_nascimento
        if isinstance(data_nascimento, str):
            try:
                return datetime.strptime(data_nascimento, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError('Data de nascimento inválida. Use o formato YYYY-MM-DD.')
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        campos = ['nome', 'sobrenome', 'cpf', 'email', 'contato', 'endereco']
        for campo in campos:
            self.fields[campo].widget.attrs.update({'class': 'form-control', 'required': True})
        self.fields['data_nascimento'].widget = DataNascimentoWidget(attrs={'class': 'form-control', 'required': True})

        if self.instance.pk:
            self.fields['tipo'] = forms.ChoiceField(
                choices=self.TIPO_USUARIO,
                widget=forms.Select(attrs={'class': 'form-control'}),
                label='Tipo de Usuário'
            )


# ----------------- ALUNO -----------------
class AlunoUsuarioForm(UsuarioBaseForm):
    class Meta(UsuarioBaseForm.Meta):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Turma = apps.get_model('cursos', 'Turma')
        Matricula = apps.get_model('cursos', 'Matricula')
        Aluno = apps.get_model('login', 'Aluno')

        self.fields['turma'] = forms.ModelMultipleChoiceField(
            queryset=Turma.objects.filter(status=True),
            required=False,
            widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input', 'data-select2': 'true'})
        )

        if self.instance.pk:
            try:
                aluno = Aluno.objects.get(usuario=self.instance)
                turmas_atuais = Turma.objects.filter(matricula__aluno=aluno, matricula__status_matricula=True)
                self.fields['turma'].initial = turmas_atuais
                self.fields['tipo'].initial = 'aluno'
            except Aluno.DoesNotExist:
                pass

    @transaction.atomic
    def save(self, commit=True):
        Aluno = apps.get_model('login', 'Aluno')
        Matricula = apps.get_model('cursos', 'Matricula')
        Turma = apps.get_model('cursos', 'Turma')

        usuario = super().save(commit=False)
        is_creating = usuario.pk is None

        if is_creating:
            usuario.tipo = 'aluno'
            usuario.status = True
            usuario.username = self.cleaned_data.get('username')
            usuario.set_password(self.cleaned_data['cpf'])

        if commit:
            usuario.save()
            if is_creating:
                aluno = Aluno.objects.create(usuario=usuario)
            else:
                aluno = Aluno.objects.get(usuario=usuario)

            turmas_selecionadas = self.cleaned_data.get('turma', [])
            Matricula.objects.filter(aluno=aluno).exclude(turma__in=turmas_selecionadas).delete()
            for turma in turmas_selecionadas:
                Matricula.objects.get_or_create(aluno=aluno, turma=turma, defaults={'status_matricula': True})

        return usuario


# ----------------- PROFESSOR -----------------
class ProfessorUsuarioForm(UsuarioBaseForm):
    class Meta(UsuarioBaseForm.Meta):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Professor = apps.get_model('login', 'Professor')
        Turma = apps.get_model('cursos', 'Turma')

        self.fields['salario'] = forms.DecimalField(max_digits=10, decimal_places=2, required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))

        if self.instance.pk:
            try:
                professor = Professor.objects.get(usuario=self.instance)
                turmas_atuais = Turma.objects.filter(professor=professor)
                self.fields['turma'] = forms.ModelMultipleChoiceField(
                    queryset=Turma.objects.filter(status=True),
                    required=False,
                    widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input', 'data-select2': 'true'}),
                    initial=turmas_atuais
                )
                self.fields['status'] = forms.BooleanField(initial=professor.status, widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
                self.fields['salario'].initial = professor.salario
                self.fields['tipo'].initial = 'professor'
            except Professor.DoesNotExist:
                pass

    @transaction.atomic
    def save(self, commit=True):
        Professor = apps.get_model('login', 'Professor')
        Turma = apps.get_model('cursos', 'Turma')

        usuario = super().save(commit=False)
        is_creating = usuario.pk is None

        if is_creating:
            usuario.tipo = 'professor'
            usuario.username = self.cleaned_data.get('username')
            usuario.set_password(self.cleaned_data['cpf'])

        if commit:
            usuario.save()
            if is_creating:
                professor = Professor.objects.create(usuario=usuario, salario=self.cleaned_data['salario'], status=True)
            else:
                professor = Professor.objects.get(usuario=usuario)
                professor.salario = self.cleaned_data['salario']
                if 'status' in self.cleaned_data:
                    professor.status = self.cleaned_data['status']
                professor.save()

            turmas_selecionadas = self.cleaned_data.get('turma', [])
            Turma.objects.filter(professor=professor).update(professor=None)
            for turma in turmas_selecionadas:
                turma.professor = professor
                turma.save()

        return usuario


# ----------------- TURMA -----------------
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

    class Meta:
        model = apps.get_model('cursos', 'Turma')
        # Não inclua 'professor' aqui
        fields = [
            "nome", "curso", "tipo",
            "entrada_horas", "saida_horas",
            "data_inicio", "data_fim",
            "dias_semana", "status"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from login.models import Professor
        self.fields['professor'] = forms.ModelChoiceField(
            queryset=Professor.objects.all(),
            required=True,
            widget=forms.Select(attrs={'class': 'form-control'})
        )


    def clean_professor(self):
        professor = self.cleaned_data.get('professor')
        if not professor:
            raise ValidationError("Selecione um professor.")
        return professor

    def save(self, commit=True):
        turma = super().save(commit=False)
        if 'dias_semana' in self.cleaned_data:
            turma.dias_semana = self.cleaned_data['dias_semana']
        turma.professor = self.cleaned_data['professor']  #  importante
        if commit:
            turma.save()
        return turma

