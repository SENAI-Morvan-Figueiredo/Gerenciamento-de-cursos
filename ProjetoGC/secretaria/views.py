from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.utils.decorators import method_decorator
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render

from .forms import AlunoUsuarioForm, ProfessorUsuarioForm, TurmaForm
from login.models import Secretaria, Aluno, Professor
from cursos.models import Turma, Matricula, Curso

from login.decorators import secretaria_required



#   <----------------- Turmas ----------------->

@method_decorator(secretaria_required, name='dispatch')
class TurmaListView(ListView):
    model = Turma
    template_name = "secretaria/turmaList.html"
    context_object_name = "turmas"

@method_decorator(secretaria_required, name='dispatch')
class TurmaDetailView(DetailView):
    model = Turma
    template_name = "secretaria/turmaDetail.html"
    context_object_name = "turma"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        turma = self.object
        context['total_alunos'] = turma.matricula_set.count()
        context['alunos_ativos'] = turma.matricula_set.filter(status_matricula=True).count()
        context['percentual_ativos'] = round((context['alunos_ativos'] / context['total_alunos'] * 100) if context['total_alunos'] > 0 else 0, 1)
        return context

@method_decorator(secretaria_required, name='dispatch')
class TurmaCreateView(CreateView):
    model = Turma
    form_class = TurmaForm
    template_name = "secretaria/turmaAdd.html"
    success_url = reverse_lazy("secretaria:turmaList")

    def form_valid(self, form):
        turma = form.save(commit=False)
        turma.professor = form.cleaned_data["professor"]
        turma.save()
        return super().form_valid(form)

@method_decorator(secretaria_required, name='dispatch')
class TurmaUpdateView(UpdateView):
    model = Turma
    form_class = TurmaForm
    template_name = "secretaria/turmaEdit.html"
    success_url = reverse_lazy("secretaria:turmaList")

    def form_valid(self, form):
        turma = form.save(commit=False)
        turma.professor = form.cleaned_data["professor"]
        turma.save()
        return super().form_valid(form)






#   <----------------- Alunos ----------------->
@method_decorator(secretaria_required, name='dispatch')
class AlunoListView(ListView):
    model = Aluno
    template_name = "secretaria/alunoList.html"
    context_object_name = "alunos"

@method_decorator(secretaria_required, name='dispatch')
class AlunoDetailView(DetailView):
    model = Aluno
    template_name = "secretaria/alunoDetail.html"
    context_object_name = "aluno"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        aluno = self.object
        context['total_turmas'] = aluno.matricula_set.count()
        context['turmas_ativas'] = aluno.matricula_set.filter(status_matricula=True).count()
        context['cursos_count'] = Curso.objects.filter(
            turma__matricula__aluno=aluno
        ).distinct().count()
        context['matricula_ativa'] = aluno.matricula_set.filter(status_matricula=True).exists()
        context['turmas_atuais'] = aluno.matricula_set.filter(status_matricula=True)
        context['historico_turmas'] = aluno.matricula_set.all().order_by('-data_ingresso')
        return context

@method_decorator(secretaria_required, name='dispatch')
class AlunoCreateView(CreateView):
    model = Aluno
    form_class = AlunoUsuarioForm
    template_name = "secretaria/alunoAdd.html"
    success_url = reverse_lazy("secretaria:alunoList")

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Aluno cadastrado com sucesso!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erro no cadastro. Verifique os dados.')
        return super().form_invalid(form)

@method_decorator(secretaria_required, name='dispatch')
class AlunoUpdateView(UpdateView):
    model = Aluno
    form_class = AlunoUsuarioForm  
    template_name = "secretaria/alunoEdit.html"
    success_url = reverse_lazy("secretaria:alunoList")

    def get_form_kwargs(self):
        """Sobrescreve para passar o Usuario como instance ao form"""
        kwargs = super().get_form_kwargs()
        # Obtém o objeto Aluno
        aluno = self.get_object()
        # Passa o Usuario relacionado como instance para o form
        kwargs['instance'] = aluno.usuario
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        messages.success(self.request, 'Aluno atualizado com sucesso!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erro na atualização. Verifique os dados.')
        return super().form_invalid(form)





#   <----------------- Professores ----------------->
@method_decorator(secretaria_required, name='dispatch')
class ProfessorListView(ListView):
    model = Professor
    template_name = "secretaria/profList.html"
    context_object_name = "professores"

@method_decorator(secretaria_required, name='dispatch')
class ProfessorDetailView(DetailView):
    model = Professor
    template_name = "secretaria/profDetail.html"
    context_object_name = "professor"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        professor = self.object
        context['total_turmas'] = professor.turma_set.count()
        context['turmas_ativas'] = professor.turma_set.filter(status=True).count()
        context['total_alunos'] = Matricula.objects.filter(
            turma__professor=professor, 
            status_matricula=True
        ).count()
        context['cursos_count'] = Curso.objects.filter(
            turma__professor=professor
        ).distinct().count()
        return context

@method_decorator(secretaria_required, name='dispatch')
class ProfessorCreateView(CreateView):
    
    model = Professor
    form_class = ProfessorUsuarioForm
    template_name = "secretaria/profAdd.html"
    success_url = reverse_lazy("secretaria:profList")

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Professor cadastrado com sucesso!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erro no cadastro. Verifique os dados.')
        return super().form_invalid(form)

@method_decorator(secretaria_required, name='dispatch')
class ProfessorUpdateView(UpdateView):
    model = Professor  # Mantemos Professor como modelo
    form_class = ProfessorUsuarioForm
    template_name = "secretaria/profEdit.html"
    success_url = reverse_lazy("secretaria:profList")

    def get_form_kwargs(self):
        """Sobrescreve para passar o Usuario como instance ao form"""
        kwargs = super().get_form_kwargs()
        # Obtém o objeto Professor
        professor = self.get_object()
        # Passa o Usuario relacionado como instance para o form
        kwargs['instance'] = professor.usuario
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Professor atualizado com sucesso!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erro na atualização. Verifique os dados.')
        return super().form_invalid(form)
    


# views.py - Adicione esta função


def config_view(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'password_change':
            # Alteração de senha
            current_password = request.POST.get('current_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            
            # Verifica se a senha atual está correta
            if not request.user.check_password(current_password):
                messages.error(request, 'Senha atual incorreta!')
            elif new_password1 != new_password2:
                messages.error(request, 'As novas senhas não coincidem!')
            elif len(new_password1) < 8:
                messages.error(request, 'A senha deve ter pelo menos 8 caracteres!')
            else:
                # Altera a senha
                request.user.set_password(new_password1)
                request.user.save()
                update_session_auth_hash(request, request.user)  # Mantém o usuário logado
                messages.success(request, 'Senha alterada com sucesso!')
                
        elif form_type == 'preferences':
            # Aqui você pode salvar preferências no banco de dados
            # Por enquanto, apenas mensagem de sucesso
            messages.success(request, 'Preferências salvas com sucesso!')
    
    context = {
        'user': request.user,
    }
    return render(request, 'secretaria/config.html', context)

        