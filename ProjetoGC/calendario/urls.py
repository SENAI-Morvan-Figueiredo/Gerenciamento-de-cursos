# Calendario/urls.py
from django.urls import path
from . import views

app_name = 'calendario'

# This module only exposes the API endpoints used by the frontend (e.g. eventos/).
# The actual top-level calendar pages (HTML) are mounted by each app (professor,
# secretaria, aluno) so the exact URLs become e.g. /professor/calendario/ and
# /secretaria/calendario/.
urlpatterns = [
    # endpoint para o FullCalendar (e.g. /professor/calendario/eventos/)
    path('eventos/', views.listar_eventos, name='listar_eventos'),
]
