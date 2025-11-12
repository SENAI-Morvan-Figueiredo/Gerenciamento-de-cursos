# Calendario/views.py
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
    """Retorna os eventos (usados pelo FullCalendar)."""
    try:
        eventos = Evento.objects.all()
        data = []
        for e in eventos:
            data.append({
                "id": e.id,
                "title": e.titulo,
                "start": e.data_fim.isoformat() if e.data_fim else None,  # 👈 mostra apenas na data final
                "description": e.descricao or "",
            })
        return JsonResponse(data, safe=False)
    except Exception as e:
        print("=== ERRO AO LISTAR EVENTOS ===")
        traceback.print_exc()
        return JsonResponse({"erro": str(e)}, status=500)
