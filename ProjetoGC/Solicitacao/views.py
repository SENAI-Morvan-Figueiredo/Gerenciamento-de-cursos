from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views import View

from .models import Solicitacao
from .forms import SolicitacaoForm
from Login.models import Secretaria
from Cursos.models import Matricula  # Import necessário para realocação

from Login.decorators import aluno_required, secretaria_required, professor_required


class SolicitacaoListView(ListView):
    model = Solicitacao
    template_name = 'Solicitacao/solicitacaoList.html'
    context_object_name = 'solicitacoes'

    def get_queryset(self):
        user = self.request.user

        if user.tipo == 'secretaria':
            return Solicitacao.objects.all().select_related(
                'turma_origem', 'turma_destino', 'turma_origem__curso', 'turma_destino__curso'
            )

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        solicitacao = form.save(commit=False)
        user = self.request.user
        solicitacao.usuario = user

        if form.cleaned_data.get('tipo') == 'realocacao':
            solicitacao.turma_origem = form.cleaned_data.get('turma_origem')
            solicitacao.turma_destino = form.cleaned_data.get('turma_destino')

        try:
            secretaria = Secretaria.objects.first()
            solicitacao.secretaria = secretaria
        except Secretaria.DoesNotExist:
            pass

        solicitacao.save()
        return super().form_valid(form)


@method_decorator(secretaria_required, name='dispatch')
class SolicitacaoStatusView(View):
    """
    View para atualizar status de solicitações com ações específicas por tipo
    """
    
    def get(self, request, pk, acao):
        solicitacao = get_object_or_404(Solicitacao, pk=pk)
        
        # Verifica se a ação é válida
        if acao not in ['aceitar', 'negar']:
            messages.error(request, "Ação inválida.")
            return redirect('solicitacao:solicitacaoList')
        
        # Apenas solicitações pendentes podem ser alteradas
        if solicitacao.status != 'pendente':
            messages.warning(request, "Esta solicitação já foi processada.")
            return redirect('solicitacao:solicitacaoList')
        
        # Processa de acordo com o tipo de solicitação
        if acao == 'aceitar':
            success = self._processar_aceitacao(solicitacao, request)
        else:  # negar
            success = self._processar_recusa(solicitacao, request)
        
        if success:
            solicitacao.status = 'aceito' if acao == 'aceitar' else 'negado'
            solicitacao.save()
            
            status_msg = "aceita" if acao == 'aceitar' else "negada"
            messages.success(request, f"Solicitação {status_msg} com sucesso!")
        else:
            messages.error(request, "Erro ao processar solicitação.")
        
        return redirect('solicitacao:solicitacaoList')
    
    def _processar_aceitacao(self, solicitacao, request):
        """
        Processa a aceitação de uma solicitação baseada no seu tipo
        """
        try:
            if solicitacao.tipo == 'realocacao':
                return self._processar_realocacao(solicitacao, request)
            
            elif solicitacao.tipo == 'trancamento':
                return self._processar_trancamento(solicitacao, request)
            
            elif solicitacao.tipo == 'declaracao':
                # Para declaração, apenas mudar o status é suficiente
                return True
                
            else:
                messages.warning(request, f"Tipo de solicitação '{solicitacao.tipo}' não reconhecido.")
                return False
                
        except Exception as e:
            messages.error(request, f"Erro ao processar solicitação: {str(e)}")
            return False
    
    def _processar_realocacao(self, solicitacao, request):
        """
        Processa realocação: move aluno da turma de origem para a turma de destino
        """
        if not solicitacao.turma_origem or not solicitacao.turma_destino:
            messages.error(request, "Dados de turma incompletos para realocação.")
            return False
        
        # Verifica se o usuário é um aluno
        if solicitacao.usuario.tipo != 'aluno':
            messages.error(request, "Realocação disponível apenas para alunos.")
            return False
        
        try:
            from Login.models import Aluno
            aluno = Aluno.objects.get(usuario=solicitacao.usuario)
            
            # Encontra a matrícula na turma de origem
            matricula = Matricula.objects.get(
                aluno=aluno, 
                turma=solicitacao.turma_origem,
                status_matricula=True
            )
            
            # Verifica se já existe matrícula na turma de destino
            matricula_existente = Matricula.objects.filter(
                aluno=aluno,
                turma=solicitacao.turma_destino,
                status_matricula=True
            ).exists()
            
            if matricula_existente:
                messages.error(request, "Aluno já está matriculado na turma de destino.")
                return False
            
            # Atualiza a matrícula para a nova turma
            matricula.turma = solicitacao.turma_destino
            matricula.save()
            
            # Atualiza dados adicionais se necessário (como professor, se for o caso)
            if solicitacao.usuario.tipo == 'professor':
                from Login.models import Professor
                professor = Professor.objects.get(usuario=solicitacao.usuario)
                # Lógica para realocação de professor se necessário
            
            return True
            
        except Matricula.DoesNotExist:
            messages.error(request, "Matrícula não encontrada na turma de origem.")
            return False
        except Aluno.DoesNotExist:
            messages.error(request, "Aluno não encontrado.")
            return False
        except Exception as e:
            messages.error(request, f"Erro na realocação: {str(e)}")
            return False
    
    def _processar_trancamento(self, solicitacao, request):
        """
        Processa trancamento: desativa matrículas do aluno
        """
        if solicitacao.usuario.tipo != 'aluno':
            messages.error(request, "Trancamento disponível apenas para alunos.")
            return False
        
        try:
            from Login.models import Aluno
            aluno = Aluno.objects.get(usuario=solicitacao.usuario)
            
            # Desativa todas as matrículas ativas do aluno
            matriculas_ativas = Matricula.objects.filter(
                aluno=aluno,
                status_matricula=True
            )
            
            if not matriculas_ativas.exists():
                messages.warning(request, "Aluno não possui matrículas ativas.")
                return True  # Considera como sucesso, pois não há nada para trancar
            
            matriculas_ativas.update(status_matricula=False)
            
            return True
            
        except Aluno.DoesNotExist:
            messages.error(request, "Aluno não encontrado.")
            return False
        except Exception as e:
            messages.error(request, f"Erro no trancamento: {str(e)}")
            return False
    
    def _processar_recusa(self, solicitacao, request):
        """
        Processa a recusa de uma solicitação (ações comuns para todos os tipos)
        """
        # Para recusa, geralmente apenas registrar o status é suficiente
        # Mas você pode adicionar lógica específica aqui se necessário
        return True