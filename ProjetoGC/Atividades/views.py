from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import TipoAtividade, Atividade
from Login.models import Professor as ProfessorModel
from Cursos.models import Turma
from django.db.models import Count, Q

@login_required
def home_atividades(request):
    """
    View para renderizar a página inicial de Atividades.
    Exibe cards para os tipos de atividades (Fixação, Avaliações, Relatórios).
    """
    
    # 1. Obter o professor logado
    try:
        professor = ProfessorModel.objects.get(usuario=request.user)
    except ProfessorModel.DoesNotExist:
        professor = None
        # Se não for professor, redirecionar ou mostrar erro. Por enquanto, apenas professor pode acessar.
        # Poderíamos implementar uma verificação mais robusta, mas seguindo a lógica do projeto.

    # 2. Obter as turmas do professor
    turmas_do_professor = Turma.objects.filter(professor=professor) if professor else Turma.objects.none()

    # 3. Obter todos os tipos de atividades
    tipos_atividades = TipoAtividade.objects.all()

    # 4. Calcular o contexto para cada tipo de atividade
    cards_context = []
    for tipo in tipos_atividades:
        # Contar todas as atividades do tipo X criadas pelo professor
        total_atividades = Atividade.objects.filter(
            turma__in=turmas_do_professor,
            tipo=tipo
        ).count()
        
        # Lógica para o card:
        # O design da imagem sugere 3 cards: Fixação, Avaliações, Relatórios.
        # Eles parecem ser links para as respectivas seções.
        
        # O ícone de check no card "Fixação" sugere que há algo "completo" ou "disponível".
        # O ícone 'A' no card "Relatórios" sugere "Análise" ou "Relatório".
        
        # Vamos manter a contagem de atividades criadas para cada tipo.
        
        count_principal = total_atividades
        label_principal = f"{count_principal} Atividades"
        
        # Ajustar a cor e ícone para corresponder ao design, se possível.
        # O modelo TipoAtividade já tem campos 'cor' e 'icone'.
        
        cards_context.append({
            'titulo': tipo.get_nome_display(),
            'cor': tipo.cor,
            'icone': tipo.icone,
            'count': count_principal,
            'label': label_principal,
            'url_visualizar': '#', # URL temporária
            'url_editar': '#', # URL temporária
        })
        
    context = {
        'cards': cards_context,
        'titulo_pagina': 'ATIVIDADES',
    }
    
    return render(request, 'Atividades/home_atividades.html', context)

from django.http import HttpResponse

@login_required
def visualizar_atividades(request, tipo_atividade):
    """
    View de placeholder para a tela de visualização de atividades por tipo.
    """
    return HttpResponse(f"<h1>Visualizar Atividades do Tipo: {tipo_atividade.capitalize()}</h1><p>Esta é uma tela de placeholder.</p>")

@login_required
def editar_atividades(request, tipo_atividade):
    """
    View de placeholder para a tela de edição/criação de atividades por tipo.
    """
    return HttpResponse(f"<h1>Editar Atividades do Tipo: {tipo_atividade.capitalize()}</h1><p>Esta é uma tela de placeholder.</p>")
