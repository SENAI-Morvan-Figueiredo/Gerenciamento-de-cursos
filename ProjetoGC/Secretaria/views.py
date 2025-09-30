from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import  Solicitacao
from Login.models import Secretaria, Aluno, Professor
from .forms import AlunoUsuarioForm, ProfessorUsuarioForm, TurmaForm
from Cursos.models import Turma

class SecretariaListView(ListView):
    model = Secretaria
    template_name = "secretaria/lista.html"
    context_object_name = "secretarias"
    
class SecretariaDetailView(DetailView):
    model = Secretaria
    template_name = "secretaria/detalhe.html"
    context_object_name = "secretaria"
    
class SecretariaCreateView(CreateView):
    model = Secretaria
    fields = ["usuario", "salario"]
    template_name = "secretaria/form.html"
    success_url = reverse_lazy("secretaria_lista")
    
class SecretariaUpdateView(UpdateView):
    model = Secretaria
    fields = ["usuario", "salario"]
    template_name = "secretaria/form.html"
    success_url = reverse_lazy("secretaria_lista")
    
class SecretariaDeleteView(DeleteView):
    model = Secretaria
    template_name = "secretaria/confrimar_exclusao.html"
    success_url = reverse_lazy("secretaria_lista")
    
class SolicitacaoListView(ListView):
    model = Solicitacao
    template_name = "secretaria/lista.html"
    context_object_name = "solicitacoes"

class SolicitacaoDetailView(DetailView):
    model = Solicitacao
    template_name = "secretaria/detalhe.html"
    context_object_name = "solicitacao"
    
class SolicitacaoCreateView(CreateView):
    model = Solicitacao
    fields = ["secretaria", "usuario", "tipo"]
    template_name = "secretaria/form.html"
    success_url = reverse_lazy("solicitacao_lista")
    
class SolicitacaoUpdateView(UpdateView):
    model = Solicitacao
    fields = ["secretaria", "usuario", "tipo"]
    template_name = "secretaria/form.html"
    success_url = reverse_lazy("solicitacao_lista")

class AlunoListView(ListView):
    model = Aluno
    template_name = "secretaria/aluno_list.html"
    context_object_name = "alunos"
    
class AlunoDetailView(DetailView):
    model = Aluno
    template_name = "secretaria/aluno_detail.html"
    context_object_name = "aluno"
    
class AlunoCreateView(CreateView):
    model = Aluno
    form_class = AlunoUsuarioForm
    template_name = "secretaria/aluno_create.html"
    success_url = reverse_lazy("aluno_lista")
    
class AlunoUpdateView(UpdateView):
    model = Aluno
    form_class = AlunoUsuarioForm  
    template_name = "secretaria/aluno_edit.html"
    success_url = reverse_lazy("aluno_lista")
    
class ProfessorListView(ListView):
    model = Professor
    template_name = "secretaria/professor_list.html"
    context_object_name = "lista_professores"
    
class ProfessorDetailView(DetailView):
    model = Professor
    template_name = "secretaria/professor_detail.html"
    context_object_name = "detail_professor"
    
class ProfessorCreateView(CreateView):
    model = Professor
    form_class = ProfessorUsuarioForm
    template_name = "secretaria/professor_create.html"
    success_url = reverse_lazy("lista_porfessores")

class ProfessorUpdateView(UpdateView):
    model = Professor
    form_class = ProfessorUsuarioForm
    template_name = "secretaria/professor_edit.html"
    success_url = reverse_lazy("lista_porfessores")  

class TurmaListView(ListView):
    model = Turma
    template_name = "secretaria/turma_list.html"
    context_object_name = "turmas"


class TurmaCreateView(CreateView):
    model = Turma
    form_class = TurmaForm
    template_name = "secretaria/turma_create.html"
    success_url = reverse_lazy("turma_lista")

    def form_valid(self, form):
        turma = form.save(commit=False)
        # atribui o professor selecionado no form
        turma.professor = form.cleaned_data["professor"]
        turma.save()
        return super().form_valid(form)


class TurmaUpdateView(UpdateView):
    model = Turma
    form_class = TurmaForm
    template_name = "secretaria/turma_edit.html"
    success_url = reverse_lazy("turma_lista")

    def form_valid(self, form):
        turma = form.save(commit=False)
        # atribui o professor selecionado no form
        turma.professor = form.cleaned_data["professor"]
        turma.save()
        return super().form_valid(form)
