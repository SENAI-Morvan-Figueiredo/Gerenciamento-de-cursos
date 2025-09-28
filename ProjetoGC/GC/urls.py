# ProjetoGC/ProjetoGC/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings # For static files in development
from django.conf.urls.static import static # For static files in development

urlpatterns = [
    path('admin/', admin.site.urls),
    path('professor/', include('Professor.urls')), # Include your Professor app's URLs here
    # path('login/', include('Login.urls')), # If you have a separate login app
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)