# models.py
from django.db import models

class Solicitacao(models.Model):
    TIPO_SOLICITACAO = [
        ('declaracao', 'Declaração'),
        ('realocacao', 'Realocação'),
        ('trancamento', 'Trancamento'),
    ]

    STATUS_BASE = [
        ('pendente', 'Pendente'),
        ('concluido', 'Concluído'),
    ]
    
    solicitacao_id = models.AutoField(primary_key=True)
    secretaria = models.ForeignKey('Login.Secretaria', on_delete=models.CASCADE)
    usuario = models.ForeignKey('Login.Usuario', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=15, choices=TIPO_SOLICITACAO)
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_BASE, default='pendente')
    
    class Meta:
        db_table = 'Solicitacao'