from django import forms
from django.utils.safestring import mark_safe
from datetime import datetime


class DataNascimentoWidget(forms.TextInput):
    """Widget customizado para entrada de data de nascimento com máscara DD/MM/YYYY"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'type': 'text',
            'inputmode': 'numeric',
            'placeholder': 'DD/MM/YYYY',
            'data-date-mask': 'true',
            'maxlength': '10'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    def format_value(self, value):
        """Converte YYYY-MM-DD para DD/MM/YYYY para exibição"""
        if not value:
            return ''
        
        # Se for uma string em formato de data
        if isinstance(value, str):
            try:
                # Tenta parsear como YYYY-MM-DD
                if len(value) == 10 and value[4] == '-' and value[7] == '-':
                    date_obj = datetime.strptime(value, '%Y-%m-%d')
                    return date_obj.strftime('%d/%m/%Y')
            except (ValueError, AttributeError):
                return value
        
        # Se for um objeto date
        try:
            return value.strftime('%d/%m/%Y')
        except (AttributeError, TypeError):
            return value
    
    def value_from_datadict(self, data, files, name):
        """Converte DD/MM/YYYY para YYYY-MM-DD para o Django"""
        value = data.get(name, '')
        
        if not value:
            return value
        
        # Remove espaços
        value = value.strip()
        
        # Valida o formato
        if len(value) == 10 and value[2] == '/' and value[5] == '/':
            try:
                day = int(value[0:2])
                month = int(value[3:5])
                year = int(value[6:10])
                
                # Converte para formato YYYY-MM-DD
                return f'{year:04d}-{month:02d}-{day:02d}'
            except (ValueError, IndexError):
                return value
        
        return value
