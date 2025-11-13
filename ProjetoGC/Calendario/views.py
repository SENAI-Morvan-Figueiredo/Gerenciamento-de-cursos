from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Login.decorators import professor_required, aluno_required, secretaria_required
from django.http import JsonResponse
from .models import Evento
import traceback

@login_required
@professor_required
def calendario_professor(request):
    """Calendário acessível para professores (com controle total)."""
    return render(request, 'calendario.html')

@login_required
@aluno_required
def calendario_aluno(request):
    """Calendário acessível para alunos (somente visualização)."""
    return render(request, 'calendario.html')

@login_required
@secretaria_required
def calendario_secretaria(request):
    """Calendário acessível para secretarias (somente visualização)."""
    return render(request, 'calendario.html')


@login_required
def listar_eventos(request):
    """
    Retorna os eventos (usados pelo FullCalendar),
    filtrando de acordo com as turmas do usuário logado.
    """
    try:
        user = request.user

        # 🔹 SECRETARIA: vê todos os eventos
        if hasattr(user, 'tipo') and user.tipo == 'secretaria':
            eventos = Evento.objects.all()

        # 🔹 PROFESSOR: vê eventos das turmas onde ele é o professor
        elif hasattr(user, 'tipo') and user.tipo == 'professor':
            # user.professor -> relação OneToOne com Professor
            eventos = Evento.objects.filter(turma__professor=user.professor)

        # 🔹 ALUNO: vê eventos das turmas onde está matriculado
        elif hasattr(user, 'tipo') and user.tipo == 'aluno':
            # user.aluno -> relação OneToOne com Aluno
            # busca as turmas onde ele está matriculado
            from Cursos.models import Matricula
  # ou o caminho real da sua app

            turmas_ids = Matricula.objects.filter(aluno=user.aluno).values_list('turma_id', flat=True)
            eventos = Evento.objects.filter(turma_id__in=turmas_ids)

        # 🔹 Caso não tenha tipo ou relação válida
        else:
            eventos = Evento.objects.none()

        # 🔹 Monta resposta JSON
        data = [
            {
                "id": e.id,
                "title": e.titulo,
                "start": e.data_inicio.isoformat() if e.data_inicio else None,
                "end": e.data_fim.isoformat() if e.data_fim else None,
                "description": e.descricao or "",
                "turma": str(e.turma) if hasattr(e, "turma") else None,
            }
            for e in eventos
        ]

        return JsonResponse(data, safe=False)

    except Exception as e:
        print("=== ERRO AO LISTAR EVENTOS ===")
        traceback.print_exc()
        return JsonResponse({"erro": str(e)}, status=500)


