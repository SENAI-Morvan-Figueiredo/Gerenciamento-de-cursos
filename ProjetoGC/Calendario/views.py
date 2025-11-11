from django.shortcuts import render
from django.http import JsonResponse
from .models import Evento
from django.contrib.auth.decorators import login_required

@login_required(login_url='/')
def calendario_view(request):
    return render(request, 'calendario.html')


@login_required
def listar_eventos(request):
    eventos = Evento.objects.all()
    data = []
    for e in eventos:
        data.append({
            "id": e.id,
            "title": e.titulo,                # FullCalendar espera 'title'
            "start": e.data_inicio.isoformat(),  # FullCalendar espera 'start'
            "end": e.data_fim.isoformat(),      # FullCalendar espera 'end'
            "description": e.descricao,
        })
    return JsonResponse(data, safe=False)

@login_required
def adicionar_evento(request):
    if not request.user.groups.filter(name__in=['Secretaria', 'Professor']).exists():
        return JsonResponse({'erro': 'Permissão negada'}, status=403)
