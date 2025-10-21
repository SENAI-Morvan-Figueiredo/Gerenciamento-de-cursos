from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),  # Placeholder view
<<<<<<< HEAD
    path("logout/", views.logout_view, name="logout"),
=======
>>>>>>> origin/secretaria
]