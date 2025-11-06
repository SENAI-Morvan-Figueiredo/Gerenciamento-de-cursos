from django.db import models

class Curso(models.Model):
    nome = models.CharField(max_length=150, unique=True, verbose_name="Nome do Curso", default="Sem Nome")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    carga_horaria = models.PositiveIntegerField(verbose_name="Carga Horária (h)", default=40)
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    disciplinas = models.ManyToManyField('Disciplina', blank=True, related_name='cursos')  # NOVO

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ["nome"]

    def __str__(self):
        return self.nome

    

class Disciplina(models.Model):
    nome = models.CharField(max_length=150, verbose_name="Nome da Disciplina", default="Sem Nome")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    carga_horaria = models.PositiveIntegerField(verbose_name="Carga Horária (h)", default=40)
    # Remova o campo curso

    def __str__(self):
        return self.nome

    

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
    nome = models.CharField(max_length=100, null=True, blank=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    professor = models.ForeignKey('Login.Professor', on_delete=models.CASCADE)

    data_inicio = models.DateField()
    data_fim = models.DateField( null=True, blank=True)
    dias_semana = models.CharField(max_length=50)
    

    entrada_horas = models.CharField(max_length=100, null=True, blank=True)
    saida_horas = models.CharField(max_length=100, null=True, blank=True)
    
    tipo = models.CharField(max_length=10, choices=TIPO_AULA)
    status = models.BooleanField(default=True)

    class Meta:
        db_table = 'Turma'
    
    def __str__(self):
        return self.nome

    

class Matricula(models.Model):
    matricula_id = models.AutoField(primary_key=True)
    aluno = models.ForeignKey('Login.Aluno', on_delete=models.CASCADE)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    data_ingresso = models.DateField(auto_now_add=True)
    status_matricula = models.BooleanField(default=True)

    class Meta:
        db_table = 'Matricula'
        unique_together = ['aluno', 'turma']

    def __str__(self):
        return f'{self.aluno} - {self.turma}'