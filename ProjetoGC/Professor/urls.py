# Professor/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.professor_home, name='professor_home'),
    # path('agenda/', views.professor_agenda, name='professor_agenda'),
    # Add other URLs for agenda, classes, diary here
]