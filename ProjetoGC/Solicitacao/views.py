from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.contrib import messages

from .models import Solicitacao
from .forms import SolicitacaoForm
from Login.models import Secretaria

from Login.decorators import aluno_required, secretaria_required, professor_required


class SolicitacaoListView(ListView):
    model = Solicitacao
    template_name = 'Solicitacao/solicitacaoList.html'
    context_object_name = 'solicitacoes'

    def get_queryset(self):
        user = self.request.user

        # Se for secretaria → vê todas
        if user.tipo == 'secretaria':
            return Solicitacao.objects.all().select_related(
                'turma_origem', 'turma_destino', 'turma_origem__curso', 'turma_destino__curso'
            )

        # Se for aluno ou professor → vê apenas as próprias
        return Solicitacao.objects.filter(usuario=user).select_related(
            'turma_origem', 'turma_destino', 'turma_origem__curso', 'turma_destino__curso'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo_usuario'] = self.request.user.tipo
        return context


@method_decorator(aluno_required or professor_required, name='dispatch')
class SolicitacaoCreateView(CreateView):
    model = Solicitacao
    form_class = SolicitacaoForm
    template_name = 'Solicitacao/solicitacaoAdd.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.tipo == 'professor':
            return reverse_lazy('professor:dashboard_professor')
        elif user.tipo == 'aluno':
            return reverse_lazy('aluno:dashboard_aluno')

    # 🔥 NOVO: Passar o user para o form
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        solicitacao = form.save(commit=False)
        user = self.request.user
        solicitacao.usuario = user

        # 🔥 CAPTURAR AS TURMAS SE FOR REALOCAÇÃO
        if form.cleaned_data.get('tipo') == 'realocacao':
            solicitacao.turma_origem = form.cleaned_data.get('turma_origem')
            solicitacao.turma_destino = form.cleaned_data.get('turma_destino')

        # pega a primeira secretaria
        try:
            secretaria = Secretaria.objects.first()
            solicitacao.secretaria = secretaria
        except Secretaria.DoesNotExist:
            pass

        solicitacao.save()
        return super().form_valid(form)

@method_decorator(secretaria_required, name='dispatch')
def update_stat_solicitacao(request, pk, acao):

    solicitacao = get_object_or_404(Solicitacao, pk=pk)

    # Apenas secretarias podem mudar o status
    if request.user.tipo != 'secretaria':
        messages.error(request, "Você não tem permissão para alterar o status.")
        return redirect('solicitacao:solicitacaoList')

    if acao == 'aceitar':
        solicitacao.status = 'aceito'
        messages.success(request, "Solicitação aceita com sucesso!")
    elif acao == 'negar':
        solicitacao.status = 'negado'
        messages.warning(request, "Solicitação negada.")
    else:
        messages.error(request, "Ação inválida.")

    solicitacao.save()
    return redirect('solicitacao:solicitacaoList')

