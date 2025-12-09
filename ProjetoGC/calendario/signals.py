# Calendario/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from atividades.models import Atividade
from .models import Evento


@receiver(post_save, sender=Atividade)
def criar_evento_ao_criar_atividade(sender, instance, created, **kwargs):
    """
    Cria automaticamente um evento no calendário quando uma nova atividade é criada.
    Garante que data_inicio e data_fim nunca sejam None (evita erro de NOT NULL).
    """
    if created:
        # Se a atividade não tiver data_entrega, usa data/hora atual
        data_evento = instance.data_entrega or timezone.now()

        Evento.objects.create(
            titulo=instance.titulo,
            descricao=instance.descricao or '',
            data_inicio=data_evento,
            data_fim=data_evento,
            turma=instance.turma,
            atividade=instance
        )
