from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Import do decorator específico do app login
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg
from Cursos.models import Turma, Matricula, Curso
from Login.models import Professor
from Atividades.models import Atividade, AtividadeEntregue
from Login.decorators import professor_required


# --- DASHBOARD DETALHADO DE UMA TURMA ---
@login_required
@professor_required
def dashboard_professor(request):
    return render(request, "Professor/Professor.html")
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
    
    # 1. Filtrar todas as turmas do professor
    turmas_professor = Turma.objects.filter(
        professor=professor,
        status=True
    ).select_related('curso')
    
    # 2. Pegar os cursos distintos dessas turmas
    cursos_ids = turmas_professor.values_list('curso_id', flat=True).distinct()
    cursos = Curso.objects.filter(id__in=cursos_ids, ativo=True).order_by('nome')
    
    # 3. Criar uma lista de tuplas (curso, turmas_do_curso)
    cursos_com_turmas = []
    for curso in cursos:
        turmas_do_curso = turmas_professor.filter(curso=curso)
        cursos_com_turmas.append({
            'curso': curso,
            'turmas': turmas_do_curso
        })

    context = {
        'cursos_com_turmas': cursos_com_turmas
    }
    
    return render(request, 'professor/listar_cursos.html', context)