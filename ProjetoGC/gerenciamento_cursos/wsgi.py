"""
WSGI config for GC project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
from django.core.wsgi import get_wsgi_application

# Atualize para o novo nome do pacote
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gerenciamento_cursos.settings')

application = get_wsgi_application()
