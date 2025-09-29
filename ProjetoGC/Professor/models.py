# models.py
from django.db import models

class Aula(models.Model):
    TIPO_AULA = [
        ('presencial', 'Presencial'),
        ('ead', 'EAD'),
    ]
    
    aula_id = models.AutoField(primary_key=True)
    turma = models.ForeignKey('Cursos.Turma', on_delete=models.CASCADE)
    data = models.DateField()
    tipo = models.CharField(max_length=10, choices=TIPO_AULA)
    
    class Meta:
        db_table = 'Aulas'

class Frequencia(models.Model):
    frequencia_id = models.AutoField(primary_key=True)
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE)
    matricula = models.ForeignKey('Cursos.Matricula', on_delete=models.CASCADE)
    presenca = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'Frequencia'
        unique_together = ['aula', 'matricula']