from django.urls import path
from .views import dashboard_professor  

app_name = 'professor'  

urlpatterns = [
    path('dashboard/', dashboard_professor, name='dashboard_professor'),
]