from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views import View
from django.db import transaction

from .models import Solicitacao
from .forms import SolicitacaoForm
from Login.models import Secretaria, Aluno , Professor
from Cursos.models import Matricula, Turma # Import necessário para realocação

from Login.decorators import aluno_required, secretaria_required, professor_required




class SolicitacaoListView(ListView):
    model = Solicitacao
    context_object_name = 'solicitacoes'

    def get_template_names(self):
        user = self.request.user
        
        if user.tipo == 'professor':
            return ['Solicitacao/solicitacaoList_professor.html']
        elif user.tipo == 'secretaria':
            return ['Solicitacao/solicitacaoList_secretaria.html']
        else:
            # Para alunos ou outros tipos, usa o template padrão
            return ['Solicitacao/solicitacaoList_secretaria.html']

    def get_queryset(self):
        user = self.request.user

        if user.tipo == 'secretaria':
            return Solicitacao.objects.all().select_related(
                'turma_origem', 'turma_destino',
            )
        else:
            return Solicitacao.objects.filter(usuario=user).select_related(
                'turma_origem', 'turma_destino',
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo_usuario'] = self.request.user.tipo
        return context

class SolicitacaoCreateView(CreateView):
    model = Solicitacao
    form_class = SolicitacaoForm
    template_name = 'Solicitacao/solicitacaoAdd.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Verifica se está autenticado
        if not request.user.is_authenticated:
            return redirect('login:login')
        
        # Verifica se é aluno OU professor
        if request.user.tipo not in ['aluno', 'professor']:
            messages.error(request, "Apenas alunos e professores podem criar solicitações.")
            return redirect('login:login')
            
        return super().dispatch(request, *args, **kwargs)
    def get_success_url(self):
        user = self.request.user
        if user.tipo == 'professor':
            return reverse_lazy('professor:home')
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


# View para atualizar status de solicitações de acordo com ações especificas da secretaria
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
        
        # Warning:Apenas solicitações pendentes podem ser alteradas
        if solicitacao.status != 'pendente':
            messages.warning(request, "Esta solicitação já foi processada.")
            return redirect('solicitacao:solicitacaoList')
        
        # Processa de acordo com o tipo de solicitação
        if acao == 'aceitar':
            result = self._processar_aceitacao(solicitacao, request)  # Mudou para 'result'
            
            # ✅ VERIFICA SE É UM REDIRECIONAMENTO
            if hasattr(result, 'status_code') and result.status_code in [301, 302]:
                return result  # Retorna o redirecionamento diretamente
            
            success = result
        else:  # negar
            success = self._processar_recusa(solicitacao, request)
        
        # ✅ SÓ EXECUTA SE NÃO FOI REDIRECIONAMENTO
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
                return True
                
            else:
                messages.warning(request, f"Tipo de solicitação '{solicitacao.tipo}' não reconhecido.")
                return False
                
        except Exception as e:
            messages.error(request, f"Erro ao processar solicitação: {str(e)}")
            return False
    
    def _processar_realocacao(self, solicitacao, request):
        """
        Processa realocação com troca segura de professores entre turmas
        """
        if not solicitacao.turma_origem or not solicitacao.turma_destino:
            messages.error(request, "Dados de turma incompletos para realocação.")
            return False
        
        if solicitacao.usuario.tipo not in ['aluno', 'professor']:
            messages.error(request, "Realocação disponível apenas para alunos e professores.")
            return False
        
        try:
            # LÓGICA PARA ALUNO (mantida igual)
            if solicitacao.usuario.tipo == 'aluno':
                aluno = Aluno.objects.get(usuario=solicitacao.usuario)
                
                matricula = Matricula.objects.get(
                    aluno=aluno, 
                    turma=solicitacao.turma_origem,
                    status_matricula=True
                )
                
                matricula_existente = Matricula.objects.filter(
                    aluno=aluno,
                    turma=solicitacao.turma_destino,
                    status_matricula=True
                ).exists()
                
                if matricula_existente:
                    messages.error(request, "Aluno já está matriculado na turma de destino.")
                    return False
                
                matricula.turma = solicitacao.turma_destino
                matricula.save()
                return True
            
            # LÓGICA PARA PROFESSOR - COM TRANSAÇÃO SEGURA
            elif solicitacao.usuario.tipo == 'professor':
                
                professor = Professor.objects.get(usuario=solicitacao.usuario)
                
                # Verifica se o professor é realmente o professor da turma de origem
                if solicitacao.turma_origem.professor != professor:
                    messages.error(request, "Você não é o professor da turma de origem.")
                    return False
                
                # Usa transação atômica para garantir que nenhuma turma fique sem professor
                with transaction.atomic():
                    # Bloqueia as turmas para evitar condições de corrida
                    turma_origem = Turma.objects.select_for_update().get(pk=solicitacao.turma_origem.pk)
                    turma_destino = Turma.objects.select_for_update().get(pk=solicitacao.turma_destino.pk)
                    
                    # Guarda os professores atuais
                    professor_origem_atual = turma_origem.professor
                    professor_destino_atual = turma_destino.professor
                    
                    # VALIDAÇÕES DE SEGURANÇA
                    if not professor_origem_atual:
                        messages.error(request, "Turma de origem não possui professor.")
                        return False
                    
                    if professor_origem_atual != professor:
                        messages.error(request, "Você não é mais o professor da turma de origem.")
                        return False
                    
                    # REALIZA A TROCA
                    # 1. Atribui o professor da origem para a destino
                    turma_destino.professor = professor_origem_atual
                    turma_destino.save()
                    
                    # 2. Atribui o professor da destino para a origem
                    turma_origem.professor = professor_destino_atual
                    turma_origem.save()
                    
                    # Mensagens informativas
                    if professor_destino_atual:
                        messages.info(request, f"Troca realizada: {professor_origem_atual.usuario.nome} para {turma_destino.nome} e {professor_destino_atual.usuario.nome} para {turma_origem.nome}")
                    else:
                        messages.info(request, f"Professor {professor_origem_atual.usuario.nome} movido para {turma_destino.nome}. Turma {turma_origem.nome} ficou sem professor.")
                
                return True
                
        except Matricula.DoesNotExist:
            messages.error(request, "Matrícula não encontrada na turma de origem.")
            return False
        except Aluno.DoesNotExist:
            messages.error(request, "Aluno não encontrado.")
            return False
        except Professor.DoesNotExist:
            messages.error(request, "Professor não encontrado.")
            return False
        except Turma.DoesNotExist:
            messages.error(request, "Turma não encontrada.")
            return False
        except Exception as e:
            messages.error(request, f"Erro na realocação: {str(e)}")
            return False
        
    def _processar_trancamento(self, solicitacao, request):
        """
        Processa trancamento: para alunos desativa matrículas, para professores redireciona para escolha de substituto
        """
        try:
            if solicitacao.usuario.tipo == 'aluno':
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
            
            elif solicitacao.usuario.tipo == 'professor':
                professor = Professor.objects.get(usuario=solicitacao.usuario)
                
                # Busca todas as turmas ativas do professor
                turmas_do_professor = Turma.objects.filter(
                    professor=professor,
                    status=True
                )
                
                if not turmas_do_professor.exists():
                    messages.warning(request, "Professor não possui turmas ativas.")
                    return True
                
                # **AQUI ESTÁ A MUDANÇA PRINCIPAL**
                # Armazena informações para redirecionamento
                request.session['trancamento_professor_id'] = professor.pk
                request.session['turmas_afetadas'] = list(turmas_do_professor.values_list('pk', flat=True))
                request.session['solicitacao_id'] = solicitacao.pk
                
                # **NÃO retorna True aqui - apenas redireciona**
                # O redirecionamento será feito pelo método get() principal
                # Retornamos um objeto de redirecionamento que será tratado no nível superior
                return redirect(reverse('solicitacao:escolher_substituto'))
                
            else:
                messages.error(request, "Trancamento disponível apenas para alunos e professores.")
                return False
                
        except Aluno.DoesNotExist:
            messages.error(request, "Aluno não encontrado.")
            return False
        except Professor.DoesNotExist:
            messages.error(request, "Professor não encontrado.")
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
    
@method_decorator(secretaria_required, name='dispatch')
class EscolherSubstitutoView(LoginRequiredMixin, TemplateView):
    template_name = 'Solicitacao/escolher_substituto.html'
    
    def get(self, request, *args, **kwargs):
        # Verifica se os dados da sessão existem
        professor_id = request.session.get('trancamento_professor_id')
        turmas_ids = request.session.get('turmas_afetadas')
        solicitacao_id = request.session.get('solicitacao_id')
        
        if not all([professor_id, turmas_ids, solicitacao_id]):
            messages.error(request, "Sessão expirada ou dados inválidos. Por favor, inicie o processo novamente.")
            return redirect('solicitacao:solicitacaoList')
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Recupera dados da sessão
        professor_id = self.request.session.get('trancamento_professor_id')
        turmas_ids = self.request.session.get('turmas_afetadas')
        solicitacao_id = self.request.session.get('solicitacao_id')
        
        if not all([professor_id, turmas_ids, solicitacao_id]):
            return context
        
        # Busca os objetos
        professor = get_object_or_404(Professor, pk=professor_id)
        turmas = Turma.objects.filter(pk__in=turmas_ids, status=True)
        solicitacao = get_object_or_404(Solicitacao, pk=solicitacao_id)
        
        # Busca professores disponíveis (excluindo o próprio professor)
        professores_disponiveis = Professor.objects.exclude(pk=professor_id).select_related('usuario')
        
        context.update({
            'professor': professor,
            'turmas': turmas,
            'solicitacao': solicitacao,
            'professores_disponiveis': professores_disponiveis,
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        professor_id = request.session.get('trancamento_professor_id')
        turmas_ids = request.session.get('turmas_afetadas')
        solicitacao_id = request.session.get('solicitacao_id')
        
        if not all([professor_id, turmas_ids, solicitacao_id]):
            messages.error(request, "Dados de sessão inválidos.")
            return redirect('solicitacao:solicitacaoList')
        
        professor_substituto_id = request.POST.get('professor_substituto')
        
        if not professor_substituto_id:
            messages.error(request, "Selecione um professor substituto.")
            return self.get(request, *args, **kwargs)
        
        try:
            professor_original = Professor.objects.get(pk=professor_id)
            professor_substituto = Professor.objects.get(pk=professor_substituto_id)
            turmas = Turma.objects.filter(pk__in=turmas_ids, status=True)
            solicitacao = Solicitacao.objects.get(pk=solicitacao_id)
            
            professor_original.status = False
            professor_original.save()
            
            # Atualiza todas as turmas com o novo professor
            turmas_atualizadas = turmas.update(professor=professor_substituto)
            
            # Limpa a sessão
            request.session.pop('trancamento_professor_id', None)
            request.session.pop('turmas_afetadas', None)
            request.session.pop('solicitacao_id', None)
            
            # **AQUI MARCA A SOLICITAÇÃO COMO ACEITA - SÓ AGORA!**
            solicitacao.status = 'aceito'
            solicitacao.save()
            
            messages.success(
                request, 
                f"Professor {professor_original.usuario.nome} removido de {turmas_atualizadas} turma(s). "
                f"Professor {professor_substituto.usuario.nome} designado como substituto."
            )
            
        except Exception as e:
            messages.error(request, f"Erro ao designar substituto: {str(e)}")
        
        return redirect('solicitacao:solicitacaoList')