from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Import do decorator específico do app login
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg
from cursos.models import Turma, Matricula, Curso
from login.models import Professor
from .models import Aula, Frequencia
from atividades.models import Atividade, AtividadeEntregue, AtividadeEntregueArquivo
from login.decorators import professor_required
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
            'atrasada': atrasada,      
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
            'entrega_id': e.pk, 
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

    return render(request, 'professor/atividade_detalhe.html', context)


@login_required
@professor_required
def atividade_entrega_detalhe(request, turma_id, atividade_id, entrega_id):
    entrega = get_object_or_404(AtividadeEntregue, pk=entrega_id)

    arquivos = AtividadeEntregueArquivo.objects.filter(
        atividade_entregue=entrega
    )

    context = {
        "entrega": entrega,
        "arquivos": arquivos,
        "atividade": entrega.atividade,
        "turma": entrega.atividade.turma,
    }

    return render(request, "professor/atividade_entrega_detalhe.html", context)


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


# --- BOLETIM ESCOLAR ---
@login_required
@professor_required
def boletim_turma(request, turma_id):
    professor = Professor.objects.get(usuario=request.user)
    turma = get_object_or_404(Turma, turma_id=turma_id, professor=professor)
    
    # Buscar todos os alunos matriculados na turma
    matriculas = Matricula.objects.filter(turma=turma).select_related('aluno__usuario')
    
    alunos_boletim = []
    soma_notas_turma = 0
    
    for matricula in matriculas:
        aluno = matricula.aluno
        usuario = aluno.usuario
        
        # Buscar todas as atividades da turma
        atividades = Atividade.objects.filter(turma=turma)
        total_atividades = atividades.count()
        
        # Calcular notas do aluno
        atividades_entregues = AtividadeEntregue.objects.filter(
            atividade__turma=turma,
            matricula=matricula
        )
        
        # Média das notas
        notas = atividades_entregues.exclude(nota__isnull=True).values_list('nota', flat=True)
        if notas:
            media_notas = sum(notas) / len(notas)
        else:
            media_notas = 0
        
        # Porcentagem de atividades entregues
        if total_atividades > 0:
            porcentagem_entregas = (atividades_entregues.count() / total_atividades * 100)
        else:
            porcentagem_entregas = 0
        
        # Calcular frequência (presença em aulas)
        total_aulas = Aula.objects.filter(turma=turma).count()
        presencas = Frequencia.objects.filter(
            aula__turma=turma,
            matricula=matricula,
            presenca=True
        ).count()
        
        if total_aulas > 0:
            frequencia_percent = (presencas / total_aulas * 100)
        else:
            frequencia_percent = 0
        
        # Calcular nota final (média ponderada: 70% notas + 30% frequência)
        nota_final = (media_notas * 0.7) + (frequencia_percent * 0.3)
        soma_notas_turma += nota_final
        
        # Determinar situação
        if nota_final >= 70 and frequencia_percent >= 75:
            situacao = "Aprovado"
            situacao_cor = "success"
        elif nota_final >= 50 and frequencia_percent >= 75:
            situacao = "Recuperação"
            situacao_cor = "warning"
        else:
            situacao = "Reprovado"
            situacao_cor = "danger"
        
        alunos_boletim.append({
            'matricula': matricula,
            'aluno_nome': f"{usuario.nome} {usuario.sobrenome}" if usuario.nome else usuario.email,
            'media_notas': round(media_notas, 1),
            'porcentagem_entregas': round(porcentagem_entregas, 1),
            'frequencia': round(frequencia_percent, 1),
            'nota_final': round(nota_final, 1),
            'situacao': situacao,
            'situacao_cor': situacao_cor,
            'total_atividades': total_atividades,
            'atividades_entregues': atividades_entregues.count(),
            'total_aulas': total_aulas,
            'presencas': presencas,
        })
    
    # Calcular média da turma
    media_turma = soma_notas_turma / len(alunos_boletim) if alunos_boletim else 0
    
    # Ordenar alunos por nota final (decrescente)
    alunos_boletim.sort(key=lambda x: x['nota_final'], reverse=True)
    
    context = {
        'turma': turma,
        'alunos_boletim': alunos_boletim,
        'media_turma': round(media_turma, 1),
        'melhor_nota': max([aluno['nota_final'] for aluno in alunos_boletim]) if alunos_boletim else 0,
        'pior_nota': min([aluno['nota_final'] for aluno in alunos_boletim]) if alunos_boletim else 0,
    }
    
    return render(request, 'professor/boletim_turma.html', context)