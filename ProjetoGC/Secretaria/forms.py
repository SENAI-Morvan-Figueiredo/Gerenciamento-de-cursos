from django import forms
from Login.models import Usuario, Aluno, Professor
from Cursos.models import Matricula, Turma, Curso



class AlunoUsuarioForm(forms.ModelForm):
    # Campos do Usuario (relacionado)
    nome = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    contato = forms.CharField(max_length=20, required=True)
    turma = forms.ModelChoiceField(
        queryset=Matricula.objects.all(),
        required=True,
        empty_label="Selecione uma turma"
    )
    cpf = forms.CharField(max_length=14, required=True)
    endereco = forms.CharField(widget=forms.Textarea, required=True)
    data_nascimento = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), required=True)
    
    
    class Meta:
        model = Aluno
        fields = ["data_ingresso"]  # só campo do Aluno mesmo
        widgets = {
            "data_ingresso": forms.DateInput(attrs={"type": "date"}),
        }

    def save(self, commit=True):
        aluno = super().save(commit=False)

    # Se já existe um usuário vinculado (edição)
        if self.instance.usuario:
            usuario = self.instance.usuario
            usuario.username = self.cleaned_data["nome"]  # ou outro campo de username
            usuario.first_name = self.cleaned_data["nome"]
            usuario.email = self.cleaned_data["email"]
            usuario.contato = self.cleaned_data["contato"]
            usuario.cpf = self.cleaned_data["cpf"]
            usuario.endereco = self.cleaned_data["endereco"]
            usuario.data_nascimento = self.cleaned_data["data_nascimento"]
            if commit:
                usuario.save()
        else:
            # Criação de um novo usuário
            usuario = Usuario.objects.create(
                username=self.cleaned_data["nome"],  
                first_name=self.cleaned_data["nome"],
                email=self.cleaned_data["email"],
                contato=self.cleaned_data["contato"],
                cpf=self.cleaned_data["cpf"],
                endereco=self.cleaned_data["endereco"],
                data_nascimento=self.cleaned_data["data_nascimento"],
                tipo="aluno"
            )
            aluno.usuario = usuario

        # Salvar a turma selecionada
        aluno.turma = self.cleaned_data["turma"]

        if commit:
            aluno.save()

        return aluno

    
class ProfessorUsuarioForm(forms.ModelForm):
    # Campos do Usuario
    nome = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    contato = forms.CharField(max_length=20, required=True)
    turmas = forms.ModelMultipleChoiceField(
        queryset=Turma.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple  # seleciona as turmas disponiveis
    )
    endereco = forms.CharField(widget=forms.Textarea, required=True)
    data_nascimento = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), required=True)

    class Meta:
        model = Professor
        fields = ["salario", "status"]  # campos do Professor

    def save(self, commit=True):
        professor = super().save(commit=False)

        # Criar o Usuario associado
        usuario = Usuario.objects.create(
            username=self.cleaned_data["nome"],
            first_name=self.cleaned_data["nome"],
            email=self.cleaned_data["email"],
            contato=self.cleaned_data["contato"],
            endereco=self.cleaned_data["endereco"],
            data_nascimento=self.cleaned_data["data_nascimento"],
            tipo="professor"
        )
        professor.usuario = usuario

        if commit:
            usuario.save()
            professor.save()

            # Associar turmas ao professor
            for turma in self.cleaned_data["turmas"]:
                turma.professor = professor
                turma.save()

        return professor

class TurmaForm(forms.ModelForm):
    # Campo virtual para nome da turma (ou usar algum campo do model, se existir)
    nome = forms.CharField(max_length=100, required=True)

    # Curso
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(),
        required=True
    )

    # Professores que dão aula
    professor = forms.ModelChoiceField(
    queryset=Professor.objects.all(),
    required=True
    )

    # Lista de alunos (apenas visualização no form, não será salvo diretamente aqui)
    alunos = forms.ModelMultipleChoiceField(
        queryset=Aluno.objects.none(),  # inicial vazio
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Alunos da turma (apenas visualização)"
    )

    class Meta:
        model = Turma
        fields = ["curso", "professor"]
