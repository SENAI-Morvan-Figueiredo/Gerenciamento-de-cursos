from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import TipoAtividade, Atividade, Avaliacao
from .forms import AvaliacaoForm
from Login.models import Professor as ProfessorModel
from Cursos.models import Turma
from django.db.models import Count, Q
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

@login_required
def home_atividades(request):
    """
    View para renderizar a página inicial de Atividades.
    Exibe cards para os tipos de atividades (Fixação, Avaliações, Relatórios).
    """
    
    # 1. Obter o professor logado
    professor = None
    if request.user.is_authenticated and request.user.tipo == 'professor':
        try:
            professor = ProfessorModel.objects.get(usuario=request.user)
        except ProfessorModel.DoesNotExist:
            professor = None
            # Se o usuário for do tipo 'professor' mas não tiver um objeto Professor associado,
            # ele será tratado como None, o que deve ser seguro para as consultas subsequentes.

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
        
        # Se o tipo for "AVALIACAO", contar as avaliações em vez de atividades
        if tipo.nome == 'AVALIACAO':
            total_atividades = Avaliacao.objects.filter(
                professor=professor,
                turma__in=turmas_do_professor
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

@login_required
def adicionar_avaliacao(request):
    """
    View para adicionar uma nova avaliacao.
    """
    if request.user.tipo != 'professor':
        return HttpResponse("Apenas professores podem criar avaliacoes.", status=403)
        
    try:
        professor = ProfessorModel.objects.get(usuario=request.user)
    except ProfessorModel.DoesNotExist:
        # Se o usuário é do tipo 'professor' mas não tem o objeto Professor, é um erro de dados.
        # Isso indica que o usuário logado não tem um perfil de professor associado, o que é um erro de configuração
        # no banco de dados. Redirecionamos para a home.
        return redirect('home') # Assumindo que 'home' é a URL de redirecionamento padrão após o login.

    
    # Obter as turmas do professor
    turmas_do_professor = Turma.objects.filter(professor=professor)
    
    if request.method == 'POST':
        form = AvaliacaoForm(professor=professor, data=request.POST, files=request.FILES)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.professor = professor
            avaliacao.save()
            return redirect('atividades:listar_avaliacoes')
    else:
        form = AvaliacaoForm(professor=professor)
    
    # A filtragem do queryset já está sendo feita no construtor do formulário.
    # Esta linha não é mais necessária, mas a deixo comentada para referência.
    # form.fields['turma'].queryset = turmas_do_professor
    
    context = {
        'form': form,
        'titulo_pagina': 'ADICIONAR AVALIACAO',
    }
    
    return render(request, 'Atividades/adicionar_avaliacao.html', context)


@login_required
def editar_avaliacao(request, avaliacao_id):
    """
    Editar uma avaliacao existente. Somente o professor dono pode editar.
    """
    if request.user.tipo != 'professor':
        return HttpResponse("Apenas professores podem editar avaliacoes.", status=403)

    try:
        professor = ProfessorModel.objects.get(usuario=request.user)
    except ProfessorModel.DoesNotExist:
        return redirect('home')

    avaliacao = get_object_or_404(Avaliacao, pk=avaliacao_id, professor=professor)

    if request.method == 'POST':
        form = AvaliacaoForm(professor=professor, data=request.POST, files=request.FILES, instance=avaliacao)
        if form.is_valid():
            form.save()
            return redirect('atividades:listar_avaliacoes')
    else:
        form = AvaliacaoForm(professor=professor, instance=avaliacao)

    context = {
        'form': form,
        'titulo_pagina': 'EDITAR AVALIACAO',
    }

    # Reutiliza o template de adicionar para o formulário de edição
    return render(request, 'Atividades/adicionar_avaliacao.html', context)


@login_required
def deletar_avaliacao(request, avaliacao_id):
    """
    Deleta uma avaliacao. Somente o professor dono pode deletar.
    Nota: o template atualmente faz a chamada via GET com confirmação em JS.
    """
    if request.user.tipo != 'professor':
        return HttpResponse("Apenas professores podem deletar avaliacoes.", status=403)

    try:
        professor = ProfessorModel.objects.get(usuario=request.user)
    except ProfessorModel.DoesNotExist:
        return redirect('home')

    avaliacao = get_object_or_404(Avaliacao, pk=avaliacao_id, professor=professor)
    # Aceitar apenas POST para exclusão por segurança
    if request.method == 'POST':
        avaliacao.delete()
        return redirect('atividades:listar_avaliacoes')
    else:
        # Método não permitido
        return HttpResponse('Method Not Allowed', status=405)

@login_required
def listar_avaliacoes(request):
    """
    View para listar as avaliacoes criadas pelo professor logado.
    """
    if request.user.tipo != 'professor':
        return HttpResponse("Apenas professores podem visualizar avaliacoes.", status=403)
        
    try:
        professor = ProfessorModel.objects.get(usuario=request.user)
    except ProfessorModel.DoesNotExist:
        # Se o usuário é do tipo 'professor' mas não tem o objeto Professor, é um erro de dados.
        # Isso indica que o usuário logado não tem um perfil de professor associado, o que é um erro de configuração
        # no banco de dados. Redirecionamos para a home.
        return redirect('home') # Assumindo que 'home' é a URL de redirecionamento padrão após o login.

    
    # Obter as turmas do professor
    turmas_do_professor = Turma.objects.filter(professor=professor)
    
    # Obter as avaliacoes do professor
    avaliacoes = Avaliacao.objects.filter(
        professor=professor,
        turma__in=turmas_do_professor
    ).order_by('-data_criacao')
    
    context = {
        'avaliacoes': avaliacoes,
        'titulo_pagina': 'AVALIACOES',
    }
    
    return render(request, 'Atividades/listar_avaliacoes.html', context)
