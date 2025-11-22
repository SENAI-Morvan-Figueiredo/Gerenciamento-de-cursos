from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import TipoAtividade, Atividade, Avaliacao
from .forms import AvaliacaoForm
from .forms_extra import AtividadeForm, EntregaForm
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


@login_required
def adicionar_atividade(request):
    """
    Permite que um professor crie uma Atividade e envie opcionalmente um arquivo.
    Se um parâmetro 'turma' for passado via GET, pré-seleciona essa turma.
    """
    if request.user.tipo != 'professor':
        return HttpResponse("Apenas professores podem criar atividades.", status=403)

    try:
        professor = ProfessorModel.objects.get(usuario=request.user)
    except ProfessorModel.DoesNotExist:
        return redirect('home')

    # Tentar obter turma do parâmetro GET (se fornecido)
    turma_id = request.GET.get('turma')
    turma_inicial = None
    if turma_id:
        try:
            turma_inicial = Turma.objects.get(turma_id=turma_id, professor=professor)
        except Turma.DoesNotExist:
            turma_inicial = None

    if request.method == 'POST':
        form = AtividadeForm(data=request.POST, files=request.FILES, professor=professor)
        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.save()
            # Se criamos a atividade a partir de uma turma específica, redirecionar
            # para a listagem de atividades daquela turma no app Professor.
            if turma_inicial:
                return redirect('professor:listar_atividades', turma_inicial.turma_id)
            # Caso contrário, voltar à home de Atividades
            return redirect('atividades:home')
    else:
        form = AtividadeForm(professor=professor)
        # Pré-selecionar a turma se foi fornecida
        if turma_inicial:
            form.fields['turma'].initial = turma_inicial

    context = {
        'form': form,
        'titulo_pagina': 'ADICIONAR ATIVIDADE',
        'turma': turma_inicial
    }
    
    return render(request, 'Atividades/adicionar_atividade.html', context)


@login_required
def lista_de_atividades(request):
    """Lista as atividades criadas pelo professor logado."""
    if request.user.tipo != 'professor':
        return HttpResponse("Apenas professores podem ver esta página.", status=403)

    try:
        professor = ProfessorModel.objects.get(usuario=request.user)
    except ProfessorModel.DoesNotExist:
        return redirect('home')

    turmas = Turma.objects.filter(professor=professor)
    atividades = Atividade.objects.filter(turma__in=turmas).order_by('-data_entrega')
    return render(request, 'Atividades/lista_de_atividades.html', {'atividades': atividades, 'titulo_pagina': 'ATIVIDADES'})


@login_required
def listar_atividades_aluno(request):
    """Lista as atividades visíveis para o aluno logado."""
    if request.user.tipo != 'aluno':
        return HttpResponse("Apenas alunos podem ver esta página.", status=403)

    # Recupera turmas do aluno via Matricula
    from Cursos.models import Matricula
    try:
        aluno = request.user.aluno
    except Exception:
        return HttpResponse('Aluno não encontrado', status=404)

    turma_ids = Matricula.objects.filter(aluno=aluno).values_list('turma_id', flat=True)
    atividades = Atividade.objects.filter(turma_id__in=turma_ids).order_by('-data_entrega')
    return render(request, 'Atividades/aluno_listar_atividades.html', {'atividades': atividades, 'titulo_pagina': 'ATIVIDADES'})


@login_required
def entregar_atividade(request, atividade_id):
    """Permite que o aluno entregue/associe arquivos a uma atividade e marque como concluída."""
    if request.user.tipo != 'aluno':
        return HttpResponse("Apenas alunos podem entregar atividades.", status=403)

    atividade = get_object_or_404(Atividade, pk=atividade_id)

    # Recupera matrícula
    from Cursos.models import Matricula
    try:
        aluno = request.user.aluno
    except Exception:
        return HttpResponse('Aluno não encontrado', status=404)

    matricula = Matricula.objects.filter(aluno=aluno, turma=atividade.turma).first()
    if not matricula:
        return HttpResponse('Aluno não matriculado nesta turma', status=403)

    # Recupera entrega existente (por aluno + atividade) ou cria nova
    entrega = AtividadeEntregue.objects.filter(atividade=atividade, matricula=matricula).first()

    if request.method == 'POST':
        form = EntregaForm(request.POST, request.FILES, instance=entrega)
        # Se o formulário contiver um arquivo enviado via campo extra, salve-o no model
        if form.is_valid():
            entrega_obj = form.save(commit=False)
            entrega_obj.atividade = atividade
            entrega_obj.matricula = matricula
            # se há arquivo enviado via FILES com campo name 'arquivo_upload'
            uploaded = request.FILES.get('arquivo_upload')
            if uploaded:
                # Salva arquivo em um novo campo url_arquivo como caminho relativo
                entrega_obj.url_arquivo = ''
                # Utilize o campo tipo_arquivo para marcar o tipo (opcional)
                # Para manter simples, salve o arquivo no campo url_arquivo com name
                entrega_obj.url_arquivo = uploaded.name
                # Também é possível salvar em FileField, mas AtividadeEntregue model uses url_arquivo (URLField).
                # Para persistir o actual file, attach it to a FileField in a future migration.
            entrega_obj.save()
            return redirect('atividades:aluno_listar_atividades')
    else:
        form = EntregaForm(instance=entrega)

    return render(request, 'Atividades/entregar_atividade.html', {'form': form, 'atividade': atividade, 'entrega': entrega})
