from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import TipoAtividade, Atividade, Avaliacao
from .forms import AvaliacaoForm
from .forms_extra import AtividadeForm, EntregaForm
from login.models import Professor as ProfessorModel
from cursos.models import Turma
from django.db.models import Count, Q
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

@login_required
def home_atividades(request):
    """
    View para renderizar a página inicial de Atividades.
    Exibe cards para os tipos de atividades (Fixação, Avaliações, Relatórios).
    """
    
    professor = None
    if request.user.is_authenticated and request.user.tipo == 'professor':
        try:
            professor = ProfessorModel.objects.get(usuario=request.user)
        except ProfessorModel.DoesNotExist:
            professor = None

    turmas_do_professor = Turma.objects.filter(professor=professor) if professor else Turma.objects.none()
    tipos_atividades = TipoAtividade.objects.all()

    cards_context = []
    for tipo in tipos_atividades:

        total_atividades = Atividade.objects.filter(
            turma__in=turmas_do_professor,
            tipo=tipo
        ).count()
        
        if tipo.nome == 'AVALIACAO':
            total_atividades = Avaliacao.objects.filter(
                professor=professor,
                turma__in=turmas_do_professor
            ).count()

        cards_context.append({
            'titulo': tipo.get_nome_display(),
            'cor': tipo.cor,
            'icone': tipo.icone,
            'count': total_atividades,
            'label': f"{total_atividades} Atividades",
            'url_visualizar': '#',
            'url_editar': '#',
        })
        
    context = {
        'cards': cards_context,
        'titulo_pagina': 'ATIVIDADES',
    }
    
    return render(request, 'Atividades/home_atividades.html', context)




@login_required
def visualizar_atividades(request, tipo_atividade):
    """ Mantida para compatibilidade com as rotas existentes """
    return HttpResponse(f"<h1>Visualizar Atividades do Tipo: {tipo_atividade.capitalize()}</h1>")


@login_required
def editar_atividades(request, tipo_atividade):
    """ Mantida para compatibilidade com as rotas existentes """
    return HttpResponse(f"<h1>Editar Atividades do Tipo: {tipo_atividade.capitalize()}</h1>")




@login_required
def adicionar_avaliacao(request):

    if request.user.tipo != 'professor':
        return HttpResponse("Apenas professores podem criar avaliacoes.", status=403)
        
    try:
        professor = ProfessorModel.objects.get(usuario=request.user)
    except ProfessorModel.DoesNotExist:
        return redirect('home')

    if request.method == 'POST':
        form = AvaliacaoForm(professor=professor, data=request.POST, files=request.FILES)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.professor = professor
            avaliacao.save()
            return redirect('atividades:listar_avaliacoes')
    else:
        form = AvaliacaoForm(professor=professor)
    
    context = {
        'form': form,
        'titulo_pagina': 'ADICIONAR AVALIACAO',
    }
    
    return render(request, 'Atividades/adicionar_avaliacao.html', context)


@login_required
def editar_avaliacao(request, avaliacao_id):

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

    return render(request, 'Atividades/adicionar_avaliacao.html', {
        'form': form,
        'titulo_pagina': 'EDITAR AVALIACAO',
    })


@login_required
def deletar_avaliacao(request, avaliacao_id):

    if request.user.tipo != 'professor':
        return HttpResponse("Apenas professores podem deletar avaliacoes.", status=403)

    try:
        professor = ProfessorModel.objects.get(usuario=request.user)
    except ProfessorModel.DoesNotExist:
        return redirect('home')

    avaliacao = get_object_or_404(Avaliacao, pk=avaliacao_id, professor=professor)
    
    if request.method == 'POST':
        avaliacao.delete()
        return redirect('atividades:listar_avaliacoes')

    return HttpResponse('Method Not Allowed', status=405)


@login_required
def listar_avaliacoes(request):

    if request.user.tipo != 'professor':
        return HttpResponse("Apenas professores podem visualizar avaliacoes.", status=403)
        
    try:
        professor = ProfessorModel.objects.get(usuario=request.user)
    except ProfessorModel.DoesNotExist:
        return redirect('home')

    turmas_do_professor = Turma.objects.filter(professor=professor)
    
    avaliacoes = Avaliacao.objects.filter(
        professor=professor,
        turma__in=turmas_do_professor
    ).order_by('-data_criacao')
    
    return render(request, 'Atividades/listar_avaliacoes.html', {
        'avaliacoes': avaliacoes,
        'titulo_pagina': 'AVALIACOES',
    })




@login_required
def adicionar_atividade(request):

    if request.user.tipo != 'professor':
        return HttpResponse("Apenas professores podem criar atividades.", status=403)

    try:
        professor = ProfessorModel.objects.get(usuario=request.user)
    except ProfessorModel.DoesNotExist:
        return redirect('home')

    turma_id = request.GET.get('turma')
    turma_inicial = None

    if turma_id:
        try:
            turma_inicial = Turma.objects.get(turma_id=turma_id, professor=professor)
        except Turma.DoesNotExist:
            turma_inicial = None

    if request.method == 'POST':
        form = AtividadeForm(
            data=request.POST,
            files=request.FILES,
            professor=professor,
            initial={'turma': turma_inicial}
        )

        if form.is_valid():
            atividade = form.save(commit=False)

            # atribui automaticamente
            if turma_inicial:
                atividade.turma = turma_inicial

            atividade.save()

            return redirect(
                'professor:listar_atividades',
                turma_id=atividade.turma.turma_id
            )

    else:
        form = AtividadeForm(professor=professor)

    return render(request, 'Atividades/adicionar_atividade.html', {
        'form': form,
        'titulo_pagina': 'ADICIONAR ATIVIDADE',
        'turma': turma_inicial
    })


@login_required
def lista_de_atividades(request):

    if request.user.tipo != 'professor':
        return HttpResponse("Apenas professores podem ver esta página.", status=403)

    try:
        professor = ProfessorModel.objects.get(usuario=request.user)
    except ProfessorModel.DoesNotExist:
        return redirect('home')

    turmas = Turma.objects.filter(professor=professor)
    atividades = Atividade.objects.filter(turma__in=turmas).order_by('-data_entrega')

    return render(request, 'Atividades/lista_de_atividades.html', {
        'atividades': atividades,
        'titulo_pagina': 'ATIVIDADES'
    })




@login_required
def listar_atividades_aluno(request):

    if request.user.tipo != 'aluno':
        return HttpResponse("Apenas alunos podem ver esta página.", status=403)

    from Cursos.models import Matricula
    try:
        aluno = request.user.aluno
    except:
        return HttpResponse('Aluno não encontrado', status=404)

    turma_ids = Matricula.objects.filter(aluno=aluno).values_list('turma_id', flat=True)
    atividades = Atividade.objects.filter(turma_id__in=turma_ids).order_by('-data_entrega')

    return render(request, 'Atividades/aluno_listar_atividades.html', {
        'atividades': atividades,
        'titulo_pagina': 'ATIVIDADES'
    })


@login_required
def entregar_atividade(request, atividade_id):

    if request.user.tipo != 'aluno':
        return HttpResponse("Apenas alunos podem entregar atividades.", status=403)

    atividade = get_object_or_404(Atividade, pk=atividade_id)

    from Cursos.models import Matricula
    try:
        aluno = request.user.aluno
    except:
        return HttpResponse('Aluno não encontrado', status=404)

    matricula = Matricula.objects.filter(aluno=aluno, turma=atividade.turma).first()
    if not matricula:
        return HttpResponse('Aluno não matriculado nesta turma', status=403)

    entrega = AtividadeEntregue.objects.filter(atividade=atividade, matricula=matricula).first()

    if request.method == 'POST':
        form = EntregaForm(request.POST, request.FILES, instance=entrega)
        if form.is_valid():
            entrega_obj = form.save(commit=False)
            entrega_obj.atividade = atividade
            entrega_obj.matricula = matricula
            uploaded = request.FILES.get('arquivo_upload')
            if uploaded:
                entrega_obj.url_arquivo = uploaded.name
            entrega_obj.save()
            return redirect('atividades:aluno_listar_atividades')

    else:
        form = EntregaForm(instance=entrega)

    return render(request, 'Atividades/entregar_atividade.html', {
        'form': form,
        'atividade': atividade,
        'entrega': entrega
    })
