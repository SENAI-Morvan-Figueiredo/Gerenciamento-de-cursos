from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Cursos.models import Turma
from Atividades.models import Atividade
from Solicitacao.models import Solicitacao
from Professor.models import Aula
from Login.models import Professor as ProfessorModel
from datetime import datetime, timedelta

@login_required
def home(request):
    """
    View para renderizar a página inicial do dashboard do professor.
    Preenche os cards com dados dinâmicos baseados no professor logado.
    """
    
    # Obter o professor logado através do usuário
    try:
        professor = ProfessorModel.objects.get(usuario=request.user)
    except ProfessorModel.DoesNotExist:
        professor = None
    
    # Contar turmas do professor
    turmas_count = 0
    if professor:
        turmas_count = Turma.objects.filter(professor=professor).count()
    
    # Contar eventos/aulas do professor (próximas 30 dias)
    eventos_count = 0
    if professor:
        data_inicio = datetime.now().date()
        data_fim = data_inicio + timedelta(days=30)
        eventos_count = Aula.objects.filter(
            turma__professor=professor,
            data__range=[data_inicio, data_fim]
        ).count()
    
    # Contar atividades do professor
    atividades_count = 0
    if professor:
        turmas = Turma.objects.filter(professor=professor)
        atividades_count = Atividade.objects.filter(turma__in=turmas).count()
    
    # Contar requisições/solicitações pendentes
    requisicoes_count = 0
    if professor:
        turmas = Turma.objects.filter(professor=professor)
        requisicoes_count = Solicitacao.objects.filter(
            turma_origem__in=turmas,
            status='pendente'
        ).count()
    
    context = {
        'turmas_count': turmas_count,
        'eventos_count': eventos_count,
        'atividades_count': atividades_count,
        'requisicoes_count': requisicoes_count,
    }
    
    return render(request, 'Professor/home.html', context)

