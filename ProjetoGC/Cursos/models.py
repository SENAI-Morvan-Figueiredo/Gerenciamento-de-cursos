# models.py
from django.db import models

class Curso(models.Model):
    curso_id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    duracao = models.DurationField()  # ou DateField dependendo da necessidade
    
    class Meta:
        db_table = 'Curso'

class Disciplina(models.Model):
    disciplina_id = models.AutoField(primary_key=True)
    materia = models.CharField(max_length=100)
    descricao = models.TextField()
    
    class Meta:
        db_table = 'Disciplina'

class GradeCurricular(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'GradeCurricular'
        unique_together = ['curso', 'disciplina']



class Turma(models.Model):
    TIPO_AULA = [
        ('presencial', 'Presencial'),
        ('semi', 'Semi-presencial'),
        ('ead', 'EAD'),
    ]
    
    turma_id = models.AutoField(primary_key=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    professor = models.ForeignKey('Login.Professor', on_delete=models.CASCADE)
    dias_semana = models.CharField(max_length=50)  # ou usar ArrayField se usar PostgreSQL
    horarios = models.CharField(max_length=100)
    data_inicio = models.DateField()
    duracao = models.DurationField()
    tipo = models.CharField(max_length=10, choices=TIPO_AULA)
    status = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'Turma'

class Matricula(models.Model):
    matricula_id = models.AutoField(primary_key=True)
    aluno = models.ForeignKey('Login.Aluno', on_delete=models.CASCADE)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    data_ingresso = models.DateField(auto_now_add=True)
    status_matricula = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'Matricula'
        unique_together = ['aluno', 'turma']