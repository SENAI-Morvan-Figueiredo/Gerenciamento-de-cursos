from django.shortcuts import render
from django.http import JsonResponse
from .models import Evento
from django.contrib.auth.decorators import login_required
import traceback

@login_required(login_url='/')
def calendario_view(request):
    return render(request, 'calendario.html')



# Calendario/views.py

@login_required
def listar_eventos(request):
    try:
        eventos = Evento.objects.all()
        data = []
        for e in eventos:
            data.append({
                "id": e.id,
                "title": e.titulo,
                "start": e.data_inicio.isoformat() if e.data_inicio else None,
                "end": e.data_fim.isoformat() if e.data_fim else None,
                "description": e.descricao or "",
            })
        return JsonResponse(data, safe=False)
    except Exception as e:
        print("=== ERRO AO LISTAR EVENTOS ===")
        traceback.print_exc()
        return JsonResponse({"erro": str(e)}, status=500)





@login_required
def adicionar_evento(request):
    # apenas secretaria e professor podem criar
    if not request.user.groups.filter(name__in=['Secretaria', 'Professor']).exists():
        return JsonResponse({'erro': 'Permissão negada'}, status=403)
