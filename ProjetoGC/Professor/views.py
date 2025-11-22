from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Import do decorator específico do app login
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg
from Cursos.models import Turma, Matricula, Curso
from Login.models import Professor
from Atividades.models import Atividade, AtividadeEntregue
from Login.decorators import professor_required
from django.utils import timezone
import datetime


# --- DASHBOARD DETALHADO DE UMA TURMA ---
@login_required
@professor_required
def dashboard_turma_detalhes(request, turma_id):
    professor = get_object_or_404(Professor, usuario=request.user)
    turma = get_object_or_404(Turma, turma_id=turma_id, professor=professor)


    # Quantidade de alunos
    total_alunos = Matricula.objects.filter(turma=turma).count()

    # Média das notas das atividades entregues
    media_notas = (
        AtividadeEntregue.objects
        .filter(atividade__turma=turma)
        .aggregate(media=Avg('nota'))
        .get('media')
    ) or 0

    # Frequência (entregas / total de atividades)
    total_atividades = Atividade.objects.filter(turma=turma).count()
    total_entregas = AtividadeEntregue.objects.filter(atividade__turma=turma).count()
    frequencia = (total_entregas / total_atividades * 100) if total_atividades > 0 else 0

    context = {
        'turma': turma,
        'total_alunos': total_alunos,
        'media_notas': round(media_notas, 2),
        'frequencia': round(frequencia, 2),
    }

    return render(request, 'professor/dashboard_turma_detalhes.html', context)


# --- LISTAGEM DE TURMAS DO PROFESSOR ---
@login_required
@professor_required
def home(request):
    professor = Professor.objects.get(usuario=request.user)
    turmas = Turma.objects.filter(professor=professor)

    context = {
        'turmas': turmas
    }
    return render(request, 'professor/home.html', context)


@login_required
@professor_required
def listar_cursos(request):
    professor = Professor.objects.get(usuario=request.user)
    
    # Filtrar todas as turmas do professor
    turmas_professor = Turma.objects.filter(
        professor=professor,
        status=True
    ).select_related('curso')
    
    # Pegar os cursos distintos dessas turmas
    cursos_ids = turmas_professor.values_list('curso_id', flat=True).distinct()
    cursos = Curso.objects.filter(id__in=cursos_ids, ativo=True).order_by('nome')
    
    # Contar turmas por curso
    cursos_com_contagem = []
    for curso in cursos:
        
        turmas_count = turmas_professor.filter(curso=curso).count()
        cursos_com_contagem.append({
            'curso': curso,
            'turmas_count': turmas_count
        })

    context = {
        'cursos_com_contagem': cursos_com_contagem
    }
    
    return render(request, 'professor/listar_cursos.html', context)

@login_required
@professor_required
def turmas_por_curso(request, curso_id):
    professor = Professor.objects.get(usuario=request.user)
    curso = get_object_or_404(Curso, id=curso_id, ativo=True)
    
    # Buscar turmas do professor para este curso específico
    turmas = Turma.objects.filter(
        professor=professor,
        curso=curso,
        status=True
    ).order_by('nome')
    
    context = {
        'curso': curso,
        'turmas': turmas
    }
    
    return render(request, 'professor/turmas_por_curso.html', context)


# --- LISTAR ATIVIDADES DA TURMA ---
@login_required
@professor_required
def listar_atividades(request, turma_id):
    professor = Professor.objects.get(usuario=request.user)
    turma = get_object_or_404(Turma, turma_id=turma_id, professor=professor)

    atividades = Atividade.objects.filter(turma=turma).order_by('-atividade_id')

    atividades_info = []
    total_alunos = Matricula.objects.filter(turma=turma).count()

    for atividade in atividades:
        entregues_qs = AtividadeEntregue.objects.filter(atividade=atividade)
        entregues_count = entregues_qs.count()

        # --- Verificar atraso ---
        hoje = timezone.now().date()

        # data_entrega pode ser datetime ou date → normalizar
        data_entrega = None
        if atividade.data_entrega:
            if isinstance(atividade.data_entrega, datetime.datetime):
                data_entrega = atividade.data_entrega.date()
            else:
                data_entrega = atividade.data_entrega

        atrasada = data_entrega and data_entrega < hoje


        atividades_info.append({
            'atividade': atividade,
            'entregues_count': entregues_count,
            'total_alunos': total_alunos,
            'atrasada': atrasada,      # <- adicionamos isso
        })

    context = {
        'turma': turma,
        'atividades_info': atividades_info
    }

    return render(request, 'professor/listar_atividades.html', context)


@login_required
@professor_required
def atividade_detalhe(request, turma_id, atividade_id):
    """
    Página detalhada da atividade com estatísticas e lista de entregas.
    """
    professor = Professor.objects.get(usuario=request.user)
    turma = get_object_or_404(Turma, turma_id=turma_id, professor=professor)
    atividade = get_object_or_404(Atividade, pk=atividade_id, turma=turma)

    entregues = AtividadeEntregue.objects.filter(atividade=atividade).select_related('matricula__aluno__usuario').order_by('-data_entrega')
    total_alunos = Matricula.objects.filter(turma=turma).count()
    total_entregues = entregues.count()
    porcentagem = (total_entregues / total_alunos * 100) if total_alunos > 0 else 0

    # Construir lista de entregas com informações úteis
    entregas_info = []
    for e in entregues:
        aluno = getattr(e.matricula, 'aluno', None)
        usuario = getattr(aluno, 'usuario', None)
        nome_aluno = usuario.nome if usuario else str(aluno)
        entregas_info.append({
            'aluno_nome': nome_aluno,
            'data_entrega': e.data_entrega,
            'nota': e.nota,
            'texto': e.texto,
            'url_arquivo': e.url_arquivo,
        })

    context = {
        'turma': turma,
        'atividade': atividade,
        'total_alunos': total_alunos,
        'total_entregues': total_entregues,
        'porcentagem': round(porcentagem, 2),
        'entregas_info': entregas_info,
    }

    return render(request, 'Professor/atividade_detalhe.html', context)


# --- LISTAR ALUNOS DA TURMA ---
@login_required
@professor_required
def listar_alunos_turma(request, turma_id):
    professor = Professor.objects.get(usuario=request.user)
    turma = get_object_or_404(Turma, turma_id=turma_id, professor=professor)
    
    matriculas = Matricula.objects.filter(turma=turma).select_related('aluno__usuario').order_by('aluno__usuario__nome')
    
    context = {
        'turma': turma,
        'matriculas': matriculas
    }
    
    return render(request, 'professor/listar_alunos_turma.html', context)