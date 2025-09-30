# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from Cursos.models import Turma

class Usuario(AbstractUser):
    TIPO_USUARIO = [
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
        ('secretaria', 'Secretaria'),
    ]
    
    usuario_id = models.AutoField(primary_key=True)
    data_nascimento = models.DateField('Data de Nascimento')
    contato = models.CharField(max_length=20, unique=True)
    cpf = models.CharField(max_length=14, unique=True)
    endereco = models.TextField('Endereço')
    tipo = models.CharField(max_length=10, choices=TIPO_USUARIO)
    
    class Meta:
        db_table = 'Usuario'


class Aluno(models.Model):
    aluno_id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    data_ingresso = models.DateField('Data de Ingresso')
   
    
    class Meta:
        db_table = 'Aluno'


class Professor(models.Model):
    professor_id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(null=False, blank=False)
    
    class Meta:
        db_table = 'Professor'


class Secretaria(models.Model):
    secretaria_id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'Secretaria'