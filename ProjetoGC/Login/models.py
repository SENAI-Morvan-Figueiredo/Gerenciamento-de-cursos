# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    TIPO_USUARIO = [
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
        ('secretaria', 'Secretaria'),
    ]
    
    usuario_id = models.AutoField(primary_key=True)
    nome = models.CharField('Nome', max_length=100, blank=True, null=True)  
    sobrenome = models.CharField('Sobrenome', max_length=100, blank=True, null=True)  
    email = models.EmailField('E-mail', unique=True, blank=True, null=True)  
    data_nascimento = models.DateField('Data de Nascimento', blank=True, null=True)  
    contato = models.CharField(max_length=20, unique=True, blank=True, null=True)  
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)  
    endereco = models.TextField('Endereço', blank=True, null=True)  
    tipo = models.CharField(max_length=10, choices=TIPO_USUARIO) 

    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['nome', 'sobrenome', 'data_nascimento', 'contato', 'cpf', 'endereco', 'tipo', 'username']


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
    
    class Meta:
        db_table = 'Professor'


class Secretaria(models.Model):
    secretaria_id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'Secretaria'