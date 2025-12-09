# C:/.../ProjetoGC/<app>/templatetags/arquivo_filters.py
import os
from django import template

register = template.Library()

@register.filter
def is_image(value):
    """
    Retorna True se `value` representar um arquivo de imagem.
    `value` pode ser:
      - uma string com o nome (ex: "foto.jpg")
      - um FileField / FieldFile (objeto com atributo .name)
      - um model instance que tenha .arquivo (FileField) ou .nome_original
    """
    if not value:
        return False

    # tentar extrair um nome de arquivo em ordem segura
    name = None

    # se for um objeto model com atributo 'arquivo' (FieldFile)
    if hasattr(value, 'arquivo'):
        # value.arquivo pode ser um FieldFile
        name = getattr(value.arquivo, 'name', None)

    # se for um FieldFile diretamente (tem .name)
    if not name and hasattr(value, 'name'):
        name = getattr(value, 'name')

    # se ainda nada, pode ser que o valor é apenas o nome original armazenado
    if not name:
        try:
            name = str(value)
        except Exception:
            name = ''

    name = (name or "").lower()

    # pegar extensão
    _, ext = os.path.splitext(name)
    ext = ext.lower()

    return ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
