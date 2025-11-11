from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendario_view, name='calendario'),
    path('eventos/', views.listar_eventos, name='listar_eventos'),
]
