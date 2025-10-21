from django.urls import path
from . import views

app_name = 'professor'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('dashboard/turma/<int:turma_id>/', views.dashboard_turma_detalhes, name='dashboard_turma_detalhes'),
]