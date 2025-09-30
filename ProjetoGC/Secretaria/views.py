from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import  Solicitacao
from Login.models import Secretaria

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
    template_name = "solicitacao/lista.html"
    context_object_name = "solicitacoes"

class SolicitacaoDetailView(DetailView):
    model = Solicitacao
    template_name = "solicitacao/detalhe.html"
    context_object_name = "solicitacao"
    
class SolicitacaoCreateView(CreateView):
    model = Solicitacao
    fields = ["secretaria", "usuario", "tipo"]
    template_name = "solicitacao/form.html"
    success_url = reverse_lazy("solicitacao_lista")
    
class SolicitacaoUpdateView(UpdateView):
    model = Solicitacao
    fields = ["secretaria", "usuario", "tipo"]
    template_name = "solicitacao/form.html"
    success_url = reverse_lazy("solicitacao_lista")
    
class SolicitacaoDeleteView(DeleteView):
    model = Solicitacao
    template_name = "solicitacao/confirmar_exclusao.html"
    success_url = reverse_lazy("solicitacao_lista")
    