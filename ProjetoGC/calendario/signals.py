# Calendario/signals.py
from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from atividades.models import Atividade
from .models import Evento


@receiver(post_save, sender=Atividade)
def criar_evento_ao_criar_atividade(sender, instance, created, **kwargs):
    """
    Cria automaticamente um evento no calendário quando uma nova atividade é criada.
    Garante que data_inicio e data_fim nunca sejam None.
    """
    if created:
        data_evento = instance.data_entrega or timezone.now()

        Evento.objects.create(
            titulo=instance.titulo,
            descricao=instance.descricao or '',
            data_inicio=data_evento,
            data_fim=data_evento,
            turma=instance.turma,
            atividade=instance
        )


@receiver(pre_save, sender=Atividade)
def set_atividade_id(sender, instance, **kwargs):
    """
    Garante que o campo atividade_id seja incremental mesmo após deletar todas as atividades.
    """
    if not instance.atividade_id:
        last_atividade = sender.objects.order_by('-atividade_id').first()
        instance.atividade_id = 1 if not last_atividade else last_atividade.atividade_id + 1


@receiver(pre_delete, sender=Atividade)
def deletar_evento_ao_deletar_atividade(sender, instance, **kwargs):
    """
    Deleta o evento correspondente quando a atividade é excluída.
    """
    Evento.objects.filter(atividade=instance).delete()
