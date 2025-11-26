# Calendario/models.py
from django.db import models
from cursos.models import Turma
from atividades.models import Atividade  # ajuste o nome do app conforme seu projeto

class Evento(models.Model):
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='eventos')
    atividade = models.OneToOneField(Atividade, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.titulo
