"""
URL configuration for GC project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('atividades/', include('Atividades.urls', namespace='atividades')),
    path('', include('Login.urls')),
    path('secretaria/', include('Secretaria.urls',  namespace='secretaria')),
    path('solicitacao/', include('Solicitacao.urls', namespace='solicitacao')),
    path('aluno/', include('Aluno.urls')),
    path('professor/', include(('Professor.urls', 'professor'), namespace='professor')),
    path('cursos/', include('Cursos.urls')),
    path('calendario/', include('Calendario.urls')), 
    path('diario/', include('Diario.urls', namespace='diario')),  
] 





