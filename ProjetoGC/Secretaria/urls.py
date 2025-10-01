from django.urls import path
from .views import dashboard_secretaria

app_name = 'secretaria'

urlpatterns = [
    path('dashboard/', dashboard_secretaria, name='dashboard_secretaria'),
]