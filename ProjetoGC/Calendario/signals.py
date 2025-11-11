# Calendario/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from Atividades.models import Atividade
from .models import Evento
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=Atividade)
def criar_evento_ao_criar_atividade(sender, instance, created, **kwargs):
    """
    Cria automaticamente um evento no calendário quando uma nova atividade é criada.
    """
    if created:
        # Tenta identificar o criador (por exemplo, professor)
        # Se não houver campo de usuário na Atividade, podemos definir um padrão
        criador = User.objects.filter(is_superuser=True).first()  # usa admin como fallback

        Evento.objects.create(
            titulo=instance.titulo,
            descricao=instance.descricao or '',
            data_inicio=instance.data_entrega,   # ou pode definir um horário inicial padrão
            data_fim=instance.data_entrega,       # usa a data de entrega como fim
            turma=instance.turma,
            criado_por=criador,
            atividade=instance
        )
