from django.shortcuts import render
from .models import Solicitacao
from .forms import SolicitacaoForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

# Create your views here.
class SolicitacaoListView(ListView):
    model = Solicitacao
    form_class = SolicitacaoForm
    

