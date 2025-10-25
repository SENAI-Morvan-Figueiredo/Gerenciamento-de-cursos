from django.urls import path
from . import views
from .views import CustomPasswordResetView
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password Reset URLs
     path(
        'password_reset/',
        CustomPasswordResetView.as_view(),
        name='password_reset'
    ),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='Login/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='Login/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='Login/password_reset_complete.html'
    ), name='password_reset_complete'),
]