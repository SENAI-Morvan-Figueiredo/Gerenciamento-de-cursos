from django.db import models

class TipoAtividade(models.Model):
    """
    Modelo para representar os tipos de atividades (Fixação, Avaliações, Relatórios),
    que serão os cards na tela principal de Atividades.
    """
    TIPO_CHOICES = [
        ('FIXACAO', 'Fixação'),
        ('AVALIACAO', 'Avaliações'),
        ('RELATORIO', 'Relatórios'),
    ]
    
    tipo_atividade_id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50, choices=TIPO_CHOICES, unique=True)
    cor = models.CharField(max_length=7, help_text="Cor em formato hexadecimal para o card.")
    icone = models.CharField(max_length=50, help_text="Classe do ícone (ex: 'fas fa-check-square').")

    class Meta:
        db_table = 'TiposAtividades'
        verbose_name = 'Tipo de Atividade'
        verbose_name_plural = 'Tipos de Atividades'

    def __str__(self):
        return self.get_nome_display()

class Avaliacao(models.Model):
    avaliacao_id = models.AutoField(primary_key=True)
    professor = models.ForeignKey('Login.Professor', on_delete=models.CASCADE)
    turma = models.ForeignKey('Cursos.Turma', on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    data_limite_entrega = models.DateTimeField()
    
    # Campos para anexo (imagem/pdf/afins)
    arquivo = models.FileField(upload_to='avaliacoes_anexos/', blank=True, null=True)
    
    class Meta:
        db_table = 'Avaliacoes'
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'

    def __str__(self):
        return self.titulo

class Atividade(models.Model):
    TIPO_ARQUIVO = [
        ('pdf', 'PDF'),
        ('doc', 'DOC'),
        ('docx', 'DOCX'),
        ('imagem', 'Imagem'),
        ('outro', 'Outro'),
    ]
    
    atividade_id = models.AutoField(primary_key=True)
    turma = models.ForeignKey('Cursos.Turma', on_delete=models.CASCADE)
    tipo = models.ForeignKey(TipoAtividade, on_delete=models.SET_NULL, null=True, blank=True) # Novo campo
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    tipo_material = models.CharField(max_length=10, choices=TIPO_ARQUIVO, blank=True, null=True)
    url_material = models.URLField(blank=True, null=True)
    data_entrega = models.DateTimeField(blank=True, null=True)
    
    # Adicionar o campo de professor para a Atividade, caso seja necessário no futuro,
    # mas por enquanto, a Avaliação já tem o professor.
    # professor = models.ForeignKey('Professor.Professor', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'Atividades'

class AtividadeEntregue(models.Model):
    atividade_entregue_id = models.AutoField(primary_key=True)
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    matricula = models.ForeignKey('Cursos.Matricula', on_delete=models.CASCADE)
    texto = models.TextField(blank=True, null=True)
    tipo_arquivo = models.CharField(max_length=10, choices=Atividade.TIPO_ARQUIVO, blank=True, null=True)
    url_arquivo = models.URLField(blank=True, null=True)
    data_entrega = models.DateTimeField(auto_now_add=True)
    nota = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    class Meta:
        db_table = 'AtividadesEntregues'
        unique_together = ['atividade', 'matricula']
