from django.shortcuts import render

# Create your views here.
# diario/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

# Importa dos models do professor
from Professor.models import Aula, Frequencia
from Cursos.models import Turma, Matricula

@login_required
def lista_turmas_diario(request):
    """Lista turmas do professor para acesso ao diário"""
    if hasattr(request.user, 'professor'):
        turmas = Turma.objects.filter(
            status=True, 
            professor__usuario=request.user
        ).select_related('curso')
    else:
        # Secretaria vê todas as turmas
        turmas = Turma.objects.filter(status=True).select_related('curso')
    
    context = {
        'turmas': turmas,
        'hoje': timezone.now().date()
    }
    return render(request, 'Diario/lista_turmas.html', context)

@login_required
def criar_aula(request, turma_id):
    """Cria uma nova aula no diário"""
    turma = get_object_or_404(Turma, pk=turma_id)
    
    # Verifica se o usuário é professor da turma
    if hasattr(request.user, 'professor') and turma.professor != request.user.professor:
        messages.error(request, 'Você não é o professor desta turma.')
        return redirect('diario:lista_turmas')
    
    if request.method == 'POST':
        data_aula = request.POST.get('data_aula')
        tipo_aula = request.POST.get('tipo_aula', 'presencial')
        
        with transaction.atomic():
            # Cria a aula APENAS com os campos que existem no modelo
            aula = Aula.objects.create(
                turma=turma,
                data=data_aula,
                tipo=tipo_aula
                # Remove conteudo e observacoes que não existem no modelo
            )
            
            # Cria registros de frequência para todos os alunos
            matriculas = Matricula.objects.filter(
                turma=turma, 
                status_matricula=True
            )
            
            for matricula in matriculas:
                Frequencia.objects.create(
                    aula=aula,
                    matricula=matricula,
                    presenca=False
                )
            
            messages.success(request, f'Aula criada com sucesso para {aula.data}!')
            return redirect('diario:registrar_chamada', aula_id=aula.aula_id)
    
    context = {
        'turma': turma,
        'hoje': timezone.now().date()
    }
    return render(request, 'Diario/criar_aula.html', context)

@login_required
def registrar_chamada(request, aula_id):
    """Página para registrar frequência dos alunos"""
    aula = get_object_or_404(Aula, pk=aula_id)
    turma = aula.turma
    
    # Verifica permissão
    if hasattr(request.user, 'professor') and aula.turma.professor != request.user.professor:
        messages.error(request, 'Você não tem permissão para acessar esta aula.')
        return redirect('diario:lista_turmas')
    
    # Busca frequências existentes
    frequencias = Frequencia.objects.filter(
        aula=aula
    ).select_related('matricula__aluno__usuario')
    
    context = {
        'aula': aula,
        'turma': turma,
        'frequencias': frequencias,
    }
    return render(request, 'Diario/registrar_chamada.html', context)

@login_required
@require_POST
def salvar_chamada(request, aula_id):
    """Salva os registros de frequência via AJAX"""
    aula = get_object_or_404(Aula, pk=aula_id)
    
    try:
        with transaction.atomic():
            presencas = request.POST.getlist('presenca[]')
            matriculas_ids = request.POST.getlist('matricula_id[]')
            observacoes = request.POST.getlist('observacao[]')
            
            for i, matricula_id in enumerate(matriculas_ids):
                matricula = get_object_or_404(Matricula, pk=matricula_id)
                
                Frequencia.objects.filter(
                    aula=aula,
                    matricula=matricula
                ).update(
                    presenca=matricula_id in presencas,
                    observacao=observacoes[i] if i < len(observacoes) else ''
                )
            
            messages.success(request, 'Chamada registrada com sucesso!')
            return JsonResponse({
                'success': True, 
                'message': 'Chamada registrada com sucesso!'
            })
    
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Erro ao registrar chamada: {str(e)}'
        })


@login_required
def historico_aulas(request, turma_id):
    """Exibe histórico de aulas de uma turma"""
    turma = get_object_or_404(Turma, pk=turma_id)
    aulas = Aula.objects.filter(turma=turma).prefetch_related('frequencia_set')
    
    # Calcular totais para cada aula
    for aula in aulas:
        # Conta presenças
        aula.presentes_count = aula.frequencia_set.filter(presenca=True).count()
        # Conta total de alunos na turma
        aula.total_alunos = aula.frequencia_set.count()
    
    context = {
        'turma': turma,
        'aulas': aulas,
    }
    return render(request, 'diario/historico_aulas.html', context)


@login_required
def relatorio_frequencia(request, turma_id):
    """Gera relatório de frequência da turma"""
    turma = get_object_or_404(Turma, pk=turma_id)
    matriculas = Matricula.objects.filter(
        turma=turma, 
        status_matricula=True
    ).select_related('aluno__usuario')
    
    # Calcula estatísticas de frequência
    aulas_total = Aula.objects.filter(turma=turma).count()
    
    total_presencas = 0
    total_faltas = 0
    total_possivel = aulas_total * matriculas.count() if matriculas.count() > 0 else 1
    
    for matricula in matriculas:
        presencas = Frequencia.objects.filter(
            matricula=matricula,
            aula__turma=turma,
            presenca=True
        ).count()
        faltas = aulas_total - presencas
        
        matricula.presencas = presencas
        matricula.faltas = faltas
        matricula.percentual = (presencas / aulas_total * 100) if aulas_total > 0 else 0
        
        total_presencas += presencas
        total_faltas += faltas
    
    # Garante que os valores sejam inteiros para o template
    total_presencas = int(total_presencas)
    total_faltas = int(total_faltas)
    total_possivel = int(total_possivel)
    
    context = {
        'turma': turma,
        'matriculas': matriculas,
        'aulas_total': aulas_total,
        'total_presencas': total_presencas,
        'total_faltas': total_faltas,
        'total_possivel': total_possivel,
    }
    return render(request, 'Diario/relatorio_frequencia.html', context)