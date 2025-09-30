from django.urls import path
from . import views  # importa views da própria app

urlpatterns = [
    path("", views.index, name="index"),  # exemplo de rota
]