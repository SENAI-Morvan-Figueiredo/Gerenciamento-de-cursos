from django.urls import path
from . import views

app_name = 'professor'  # importante para usar namespaced URLs

urlpatterns = [
    path('', views.home, name='home'),
]
