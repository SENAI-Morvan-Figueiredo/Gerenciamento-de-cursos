from django.db import models
from django.conf import settings

from Cursos.models import Turma  # se já tiver o modelo de turma

class Evento(models.Model):
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='eventos')
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


    def __str__(self):
        return self.titulo
