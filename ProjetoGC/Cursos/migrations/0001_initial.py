
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Login', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Disciplina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(default='Sem Nome', max_length=150, verbose_name='Nome da Disciplina')),
                ('descricao', models.TextField(blank=True, verbose_name='Descrição')),
                ('carga_horaria', models.PositiveIntegerField(default=40, verbose_name='Carga Horária (h)')),
            ],
        ),
        migrations.CreateModel(
            name='Turma',
            fields=[
                ('turma_id', models.AutoField(primary_key=True, serialize=False)),
                ('nome', models.CharField(blank=True, max_length=100, null=True)),
                ('dias_semana', models.CharField(max_length=50)),
                ('horarios', models.CharField(max_length=100)),
                ('data_inicio', models.DateField()),
                ('duracao', models.DurationField()),
                ('tipo', models.CharField(choices=[('presencial', 'Presencial'), ('semi', 'Semi-presencial'), ('ead', 'EAD')], max_length=10)),
                ('status', models.BooleanField(default=True)),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Cursos.curso')),
                ('professor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Login.professor')),
            ],
            options={
                'db_table': 'Turma',
            },
        ),
        migrations.CreateModel(
            name='Curso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(default='Sem Nome', max_length=150, unique=True, verbose_name='Nome do Curso')),
                ('descricao', models.TextField(blank=True, verbose_name='Descrição')),
                ('carga_horaria', models.PositiveIntegerField(default=40, verbose_name='Carga Horária (h)')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('disciplinas', models.ManyToManyField(blank=True, related_name='cursos', to='Cursos.disciplina')),
            ],
            options={
                'verbose_name': 'Curso',
                'verbose_name_plural': 'Cursos',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='GradeCurricular',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Cursos.curso')),
                ('disciplina', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Cursos.disciplina')),
            ],
            options={
                'db_table': 'GradeCurricular',
                'unique_together': {('curso', 'disciplina')},
            },
        ),
        migrations.CreateModel(
            name='Matricula',
            fields=[
                ('matricula_id', models.AutoField(primary_key=True, serialize=False)),
                ('data_ingresso', models.DateField(auto_now_add=True)),
                ('status_matricula', models.BooleanField(default=True)),
                ('aluno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Login.aluno')),
                ('turma', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Cursos.turma')),
            ],
            options={
                'db_table': 'Matricula',
                'unique_together': {('aluno', 'turma')},
            },
        ),
    ]
