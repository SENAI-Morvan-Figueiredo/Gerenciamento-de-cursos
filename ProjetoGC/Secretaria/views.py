from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from .forms import AlunoUsuarioForm, ProfessorUsuarioForm, TurmaForm
from .models import Solicitacao
from Login.models import Secretaria, Aluno, Professor
from Cursos.models import Turma

from Login.decorators import secretaria_required

#   <----------------- Turmas ----------------->

@method_decorator(secretaria_required, name='dispatch')
class TurmaListView(ListView):
    model = Turma
    template_name = "secretaria/turmaList.html"
    context_object_name = "turmas"

@method_decorator(secretaria_required, name='dispatch')
class TurmaDetailView(DetailView):
    model = Turma
    template_name = "secretaria/turmaDetail.html"
    context_object_name = "turma"

@method_decorator(secretaria_required, name='dispatch')
class TurmaCreateView(CreateView):
    model = Turma
    form_class = TurmaForm
    template_name = "secretaria/turmaAdd.html"
    success_url = reverse_lazy("secretaria:turmaList")

    def form_valid(self, form):
        turma = form.save(commit=False)
        turma.professor = form.cleaned_data["professor"]
        turma.save()
        return super().form_valid(form)

@method_decorator(secretaria_required, name='dispatch')
class TurmaUpdateView(UpdateView):
    model = Turma
    form_class = TurmaForm
    template_name = "secretaria/turmaEdit.html"
    success_url = reverse_lazy("secretaria:turmaList")

    def form_valid(self, form):
        turma = form.save(commit=False)
        turma.professor = form.cleaned_data["professor"]
        turma.save()
        return super().form_valid(form)

#   <----------------- Alunos ----------------->
@method_decorator(secretaria_required, name='dispatch')
class AlunoListView(ListView):
    model = Aluno
    template_name = "secretaria/alunoList.html"
    context_object_name = "alunos"

@method_decorator(secretaria_required, name='dispatch')
class AlunoDetailView(DetailView):
    model = Aluno
    template_name = "secretaria/alunoDetail.html"
    context_object_name = "aluno"

@method_decorator(secretaria_required, name='dispatch')
class AlunoCreateView(CreateView):
    model = Aluno
    form_class = AlunoUsuarioForm
    template_name = "secretaria/alunoAdd.html"
    success_url = reverse_lazy("secretaria:alunoList")

@method_decorator(secretaria_required, name='dispatch')
class AlunoUpdateView(UpdateView):
    model = Aluno
    form_class = AlunoUsuarioForm  
    template_name = "secretaria/alunoEdit.html"
    success_url = reverse_lazy("secretaria:alunoList")

#   <----------------- Professores ----------------->
@method_decorator(secretaria_required, name='dispatch')
class ProfessorListView(ListView):
    model = Professor
    template_name = "secretaria/profList.html"
    context_object_name = "professores"

@method_decorator(secretaria_required, name='dispatch')
class ProfessorDetailView(DetailView):
    model = Professor
    template_name = "secretaria/profDetail.html"
    context_object_name = "professor"

@method_decorator(secretaria_required, name='dispatch')
class ProfessorCreateView(CreateView):
    model = Professor
    form_class = ProfessorUsuarioForm
    template_name = "secretaria/profAdd.html"
    success_url = reverse_lazy("secretaria:profList")

@method_decorator(secretaria_required, name='dispatch')
class ProfessorUpdateView(UpdateView):
    model = Professor
    form_class = ProfessorUsuarioForm
    template_name = "secretaria/profEdit.html"
    success_url = reverse_lazy("secretaria:profList")