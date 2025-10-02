from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy

from .forms import AlunoUsuarioForm, ProfessorUsuarioForm, TurmaForm

from .models import  Solicitacao
from Login.models import Secretaria, Aluno, Professor
from Cursos.models import Turma


#   <----------------- Turmas ----------------->
class TurmaListView(ListView):
    model = Turma
    template_name = "secretaria/turmaList.html"
    context_object_name = "turmas"

class TurmaCreateView(CreateView):
    model = Turma
    form_class = TurmaForm
    template_name = "secretaria/turmaAdd.html"
    success_url = reverse_lazy("turmaLista")

    def form_valid(self, form):
        turma = form.save(commit=False)
        # atribui o professor selecionado no form
        turma.professor = form.cleaned_data["professor"]
        turma.save()
        return super().form_valid(form)

class TurmaUpdateView(UpdateView):
    model = Turma
    form_class = TurmaForm
    template_name = "secretaria/turmaEdit.html"
    success_url = reverse_lazy("turmaLista")

    def form_valid(self, form):
        turma = form.save(commit=False)
        # atribui o professor selecionado no form
        turma.professor = form.cleaned_data["professor"]
        turma.save()
        return super().form_valid(form)
    

#   <----------------- Alunos ----------------->
class AlunoListView(ListView):
    model = Aluno
    template_name = "secretaria/alunoList.html"
    context_object_name = "alunos"
    
class AlunoDetailView(DetailView):
    model = Aluno
    template_name = "secretaria/alunoDetail.html"
    context_object_name = "aluno"
    
class AlunoCreateView(CreateView):
    model = Aluno
    form_class = AlunoUsuarioForm
    template_name = "secretaria/alunoAdd.html"
    success_url = reverse_lazy("alunoList")
    
class AlunoUpdateView(UpdateView):
    model = Aluno
    form_class = AlunoUsuarioForm  
    template_name = "secretaria/alunoEdit.html"
    success_url = reverse_lazy("alunoList")


#   <----------------- Professores ----------------->
class ProfessorListView(ListView):
    model = Professor
    template_name = "secretaria/profList.html"
    context_object_name = "professores"
    
class ProfessorDetailView(DetailView):
    model = Professor
    template_name = "secretaria/profDetail.html"
    context_object_name = "professor"
    
class ProfessorCreateView(CreateView):
    model = Professor
    form_class = ProfessorUsuarioForm
    template_name = "secretaria/profAdd.html"
    success_url = reverse_lazy("porfList")

class ProfessorUpdateView(UpdateView):
    model = Professor
    form_class = ProfessorUsuarioForm
    template_name = "secretaria/profEdit.html"
    success_url = reverse_lazy("profList")  


#   <----------------- Funcionários Secretaria ----------------->
# class SecretariaListView(ListView):
#     model = Secretaria
#     template_name = "secretaria/lista.html"
#     context_object_name = "secretarias"
    
# class SecretariaDetailView(DetailView):
#     model = Secretaria
#     template_name = "secretaria/detalhe.html"
#     context_object_name = "secretaria"
    
# class SecretariaCreateView(CreateView):
#     model = Secretaria
#     fields = ["usuario", "salario"]
#     template_name = "secretaria/form.html"
#     success_url = reverse_lazy("secretaria_lista")
    
# class SecretariaUpdateView(UpdateView):
#     model = Secretaria
#     fields = ["usuario", "salario"]
#     template_name = "secretaria/form.html"
#     success_url = reverse_lazy("secretaria_lista")
    
# class SecretariaDeleteView(DeleteView):
#     model = Secretaria
#     template_name = "secretaria/confrimar_exclusao.html"
#     success_url = reverse_lazy("secretaria_lista")


#   <----------------- Solicitação ----------------->
# class SolicitacaoListView(ListView):
#     model = Solicitacao
#     template_name = "secretaria/lista.html"
#     context_object_name = "solicitacoes"

# class SolicitacaoDetailView(DetailView):
#     model = Solicitacao
#     template_name = "secretaria/detalhe.html"
#     context_object_name = "solicitacao"
    
# class SolicitacaoCreateView(CreateView):
#     model = Solicitacao
#     fields = ["secretaria", "usuario", "tipo"]
#     template_name = "secretaria/form.html"
#     success_url = reverse_lazy("solicitacao_lista")
    
# class SolicitacaoUpdateView(UpdateView):
#     model = Solicitacao
#     fields = ["secretaria", "usuario", "tipo"]
#     template_name = "secretaria/form.html"
#     success_url = reverse_lazy("solicitacao_lista")
