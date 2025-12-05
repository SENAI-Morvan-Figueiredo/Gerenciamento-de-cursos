from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, JsonResponse
from login.decorators import aluno_required
from cursos.models import Matricula, Turma
from atividades.models import Atividade, AtividadeEntregue, AtividadeEntregueArquivo
from calendario.models import Evento
from django.utils import timezone
from datetime import timedelta, datetime
import json

@login_required
@aluno_required
def dashboard_aluno(request):
    """Dashboard principal EXCLUSIVO para alunos"""
    try:
        aluno = request.user.aluno
    except:
        return render(request, "aluno/error.html", {
            "message": "Perfil de aluno não encontrado. Contate a secretaria."
        })
    
    # Turmas do aluno
    matriculas = Matricula.objects.filter(aluno=aluno, status_matricula=True)
    turmas = [matricula.turma for matricula in matriculas]
    
    # Todas as atividades do aluno
    todas_atividades = Atividade.objects.filter(turma__in=turmas)
    
    # Calcular status das atividades
    atividades_com_status = []
    for atividade in todas_atividades:
        entrega = AtividadeEntregue.objects.filter(
            atividade=atividade,
            matricula__aluno=aluno
        ).first()
        
        if entrega:
            status = 'entregue'
        elif atividade.data_entrega and atividade.data_entrega < timezone.now():
            status = 'atrasado'
        else:
            status = 'pendente'
            
        atividades_com_status.append({
            'atividade': atividade,
            'status': status,
            'entrega': entrega
        })
    
    # Estatísticas
    atividades_pendentes = len([a for a in atividades_com_status if a['status'] == 'pendente'])
    atividades_entregues = len([a for a in atividades_com_status if a['status'] == 'entregue'])
    
    # Próximas atividades (próximos 7 dias)
    sete_dias = timezone.now() + timedelta(days=7)
    proximas_atividades = [
        a for a in atividades_com_status 
        if a['status'] == 'pendente' and a['atividade'].data_entrega and a['atividade'].data_entrega <= sete_dias
    ][:5]
    
    # Próximos eventos
    proximos_eventos = Evento.objects.filter(
        turma__in=turmas,
        data_inicio__gte=timezone.now()
    ).order_by('data_inicio')[:3]
    
    # Eventos de hoje
    hoje = timezone.now().date()
    eventos_hoje = Evento.objects.filter(
        turma__in=turmas,
        data_inicio__date=hoje
    ).count()
    
    context = {
        'turmas': turmas,
        'turmas_count': len(turmas),
        'atividades_pendentes': atividades_pendentes,
        'atividades_entregues': atividades_entregues,
        'proximas_atividades': proximas_atividades,
        'proximos_eventos': proximos_eventos,
        'eventos_hoje': eventos_hoje,
        'data_atual': timezone.now(),
    }
    
    return render(request, "aluno/dashboard.html", context)

@login_required
@aluno_required
def minhas_turmas(request):
    """Página com lista de todas as turmas do aluno"""
    try:
        aluno = request.user.aluno
    except:
        return render(request, "aluno/error.html", {
            "message": "Perfil de aluno não encontrado."
        })
    
    matriculas = Matricula.objects.filter(aluno=aluno, status_matricula=True)
    turmas = [matricula.turma for matricula in matriculas]
    
    # Adicionar informações extras para cada turma
    turmas_com_info = []
    total_pendentes_geral = 0
    total_atividades_geral = 0
    
    for turma in turmas:
        atividades_turma = Atividade.objects.filter(turma=turma)
        atividades_pendentes = atividades_turma.filter(
            data_entrega__gte=timezone.now()
        ).count()
        
        total_atividades = atividades_turma.count()
        total_pendentes_geral += atividades_pendentes
        total_atividades_geral += total_atividades
        
        turmas_com_info.append({
            'turma': turma,
            'atividades_pendentes': atividades_pendentes,
            'total_atividades': total_atividades,
        })
    
    # Calcular estatísticas gerais
    total_concluidas = total_atividades_geral - total_pendentes_geral
    progresso_geral = f"{total_concluidas}/{total_atividades_geral}" if total_atividades_geral > 0 else "0"
    
    context = {
        'turmas_com_info': turmas_com_info,
        'total_turmas': len(turmas_com_info),
        'total_pendentes_geral': total_pendentes_geral,
        'total_atividades_geral': total_atividades_geral,
        'total_concluidas': total_concluidas,
        'progresso_geral': progresso_geral,
    }
    
    return render(request, "aluno/minhas_turmas.html", context)

@login_required
@aluno_required
def detalhes_turma(request, turma_id):
    """Detalhes de uma turma específica"""
    turma = get_object_or_404(Turma, turma_id=turma_id)
    
    # Verificar se o aluno está matriculado
    matricula = Matricula.objects.filter(
        aluno=request.user.aluno, 
        turma=turma, 
        status_matricula=True
    ).first()
    
    if not matricula:
        return render(request, "aluno/error.html", {
            "message": "Você não está matriculado nesta turma."
        })
    
    # Atividades da turma
    atividades = Atividade.objects.filter(turma=turma).order_by('-data_entrega')
    
    # Verificar status de entrega
    atividades_com_status = []
    for atividade in atividades:
        entrega = AtividadeEntregue.objects.filter(
            atividade=atividade,
            matricula__aluno=request.user.aluno
        ).first()
        
        if entrega:
            status = 'entregue'
        elif atividade.data_entrega and atividade.data_entrega < timezone.now():
            status = 'atrasado'
        else:
            status = 'pendente'
            
        atividades_com_status.append({
            'atividade': atividade,
            'status': status,
            'entrega': entrega
        })
    
    # Próximos eventos da turma
    proximos_eventos = Evento.objects.filter(
        turma=turma,
        data_inicio__gte=timezone.now()
    ).order_by('data_inicio')[:5]
    
    context = {
        'turma': turma,
        'atividades_com_status': atividades_com_status,
        'proximos_eventos': proximos_eventos,
        'professor': turma.professor,
    }
    
    return render(request, "aluno/detalhes_turma.html", context)

@login_required
@aluno_required
def lista_atividades(request):
    """Lista todas as atividades do aluno"""
    try:
        aluno = request.user.aluno
    except:
        return render(request, "aluno/error.html", {
            "message": "Perfil de aluno não encontrado."
        })
    
    # Turmas do aluno
    turma_ids = Matricula.objects.filter(
        aluno=aluno, 
        status_matricula=True
    ).values_list('turma_id', flat=True)
    
    # Todas as atividades
    atividades = Atividade.objects.filter(turma_id__in=turma_ids).order_by('-data_entrega')
    
    # Adicionar status
    atividades_com_status = []
    for atividade in atividades:
        entrega = AtividadeEntregue.objects.filter(
            atividade=atividade,
            matricula__aluno=aluno
        ).first()
        
        if entrega:
            status = 'entregue'
        elif atividade.data_entrega and atividade.data_entrega < timezone.now():
            status = 'atrasado'
        else:
            status = 'pendente'
            
        atividades_com_status.append({
            'atividade': atividade,
            'status': status,
            'entrega': entrega
        })
    
    # Turmas para filtro
    turmas = Turma.objects.filter(turma_id__in=turma_ids)
    
    context = {
        'atividades': atividades_com_status,
        'turmas': turmas,
    }
    
    return render(request, "aluno/lista_atividades.html", context)

@login_required
@aluno_required
def entregar_atividade(request, atividade_id):
    """Entrega de atividade pelo aluno"""
    atividade = get_object_or_404(Atividade, atividade_id=atividade_id)

    matricula = Matricula.objects.filter(
        aluno=request.user.aluno,
        turma=atividade.turma,
        status_matricula=True
    ).first()

    if not matricula:
        return render(request, "aluno/error.html", {
            "message": "Você não está matriculado na turma desta atividade."
        })

    entrega = AtividadeEntregue.objects.filter(
        atividade=atividade,
        matricula=matricula
    ).first()

    if request.method == 'POST':
        texto = request.POST.get('texto', '').strip()
        url = request.POST.get('url_arquivo', '').strip()

        # Se já existe, atualiza. Se não, cria a entrega.
        if entrega:
            entrega.texto = texto
            entrega.url_arquivo = url if url else None
            entrega.data_entrega = timezone.now()
            entrega.save()
            print(f"Entrega atualizada: {entrega.id}")
        else:
            entrega = AtividadeEntregue.objects.create(
                atividade=atividade,
                matricula=matricula,
                texto=texto,
                url_arquivo=url if url else None,
                data_entrega=timezone.now()
            )
            print(f"Nova entrega criada: {entrega.id}")

        # ARQUIVOS MULTIPLOS
        arquivos = request.FILES.getlist('arquivos')
        for arquivo in arquivos:
            obj_arquivo = AtividadeEntregueArquivo.objects.create(
                atividade_entregue=entrega,
                arquivo=arquivo,
                nome_original=arquivo.name
            )
            print("Arquivo salvo:", obj_arquivo.nome_original)
            print("Caminho completo no servidor:", obj_arquivo.arquivo.path)

        # Redireciona para a própria página para mostrar os arquivos enviados
        return redirect('aluno:entregar_atividade', atividade_id=atividade.atividade_id)

    context = {
        'atividade': atividade,
        'entrega': entrega,
        'turma': atividade.turma,
        'now': timezone.now(),
    }

    return render(request, "aluno/entregar_atividade.html", context)



@login_required
@aluno_required
def calendario_aluno(request):
    """Calendário do aluno"""
    return render(request, "aluno/calendario.html")

@login_required
@aluno_required
def solicitacoes_aluno(request):
    """Página de solicitações do aluno"""
    return render(request, "aluno/solicitacoes.html")

@login_required
@aluno_required
def perfil_aluno(request):
    """Perfil do aluno"""
    try:
        aluno = request.user.aluno
        usuario = request.user
    except:
        return render(request, "aluno/error.html", {
            "message": "Perfil de aluno não encontrado."
        })
    
    context = {
        'aluno': aluno,
        'usuario': usuario,
    }
    
    return render(request, "aluno/perfil.html", context)

# API para eventos do calendário (exclusiva para aluno)
@login_required
@aluno_required
def eventos_aluno_api(request):
    """API para eventos do calendário do aluno"""
    try:
        aluno = request.user.aluno
        turma_ids = Matricula.objects.filter(
            aluno=aluno, 
            status_matricula=True
        ).values_list('turma_id', flat=True)
        
        eventos = Evento.objects.filter(turma_id__in=turma_ids)
        
        eventos_data = []
        for evento in eventos:
            eventos_data.append({
                'id': evento.id,
                'title': evento.titulo,
                'start': evento.data_inicio.isoformat(),
                'end': evento.data_fim.isoformat() if evento.data_fim else None,
                'description': evento.descricao,
                'turma': evento.turma.nome,
                'color': '#3b82f6',  # Cor padrão para eventos do aluno
            })
        
        return JsonResponse(eventos_data, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)