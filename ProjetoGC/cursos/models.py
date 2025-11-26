from django.db import models

class Curso(models.Model):
    nome = models.CharField(max_length=150, unique=True, verbose_name="Nome do Curso", default="Sem Nome")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    carga_horaria = models.PositiveIntegerField(verbose_name="Carga Horária (h)", default=40)
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    disciplinas = models.ManyToManyField('Disciplina', through='GradeCurricular', blank=True, related_name='cursos')

    class Meta:
        verbose_name = "curso"
        verbose_name_plural = "cursos"
        ordering = ["nome"]

    def __str__(self):
        return self.nome if self.nome else "Curso sem nome"

    

class Disciplina(models.Model):
    nome = models.CharField(max_length=150, verbose_name="Nome da Disciplina", default="Sem Nome")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    carga_horaria = models.PositiveIntegerField(verbose_name="Carga Horária (h)", default=40)

    def __str__(self):
        return self.nome if self.nome else "Disciplina sem nome"

    
class AlocacaoProfessor(models.Model):
    professor = models.ForeignKey('login.professor', on_delete=models.CASCADE)
    Curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    class Meta:
        db_table = 'Cursos_alocacaoprofessor'  
        verbose_name = "Alocação de Professor"
        verbose_name_plural = "Alocações de Professores"

    def __str__(self):
        return f"{self.professor} - {self.curso}"

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

    professor = models.ForeignKey('login.professor', on_delete=models.SET_NULL,  # Ou models.SET_DEFAULT
        null=True,                  # Permite NULL
        blank=True,
        default=None)


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
        if self.nome and self.curso:
            return f"{self.nome} - {self.curso.nome}"
        elif self.nome:
            return self.nome
        elif self.curso:
            return f"Turma - {self.curso.nome}"
        else:
            return "Turma sem nome"  # Fallback seguro

    

class Matricula(models.Model):
    matricula_id = models.AutoField(primary_key=True)
    aluno = models.ForeignKey('login.aluno', on_delete=models.CASCADE)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    data_ingresso = models.DateField(auto_now_add=True)
    status_matricula = models.BooleanField(default=True)

    class Meta:
        db_table = 'Matricula'
        unique_together = ['aluno', 'turma']

    def __str__(self):
        return f'{self.aluno} - {self.turma}'