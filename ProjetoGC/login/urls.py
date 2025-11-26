from django.urls import path
from . import views
from .views import CustomPasswordResetView
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .forms import CustomSetPasswordForm  # Add this import

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('password_reset/', CustomPasswordResetView.as_view(
        template_name='Login/password_reset_form.html',
        email_template_name='Login/password_reset_email.html',
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),
    
    path('password_reset/done/', views.password_reset_done, name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='Login/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete'),
        form_class=CustomSetPasswordForm
    ), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='Login/password_reset_complete.html'
    ), name='password_reset_complete'),
]