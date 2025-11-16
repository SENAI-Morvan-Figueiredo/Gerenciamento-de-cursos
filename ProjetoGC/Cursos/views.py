from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Curso, Disciplina
from .forms import CursoForm, DisciplinaForm

# ==========================
# CURSOS
# ==========================
class CursoListView(ListView):
    model = Curso
    template_name = "Cursos/curso_list.html"
    context_object_name = "cursos"


class CursoCreateView(CreateView):
    model = Curso
    form_class = CursoForm
    template_name = "Cursos/curso_form.html"
    success_url = reverse_lazy("curso_list")

    def form_valid(self, form):
        messages.success(self.request, "Curso criado com sucesso!")
        return super().form_valid(form)

class CursoUpdateView(UpdateView):
    model = Curso
    form_class = CursoForm
    template_name = "Cursos/curso_edit.html"
    success_url = reverse_lazy("curso_list")

    def get_initial(self):
        initial = super().get_initial()
        initial['disciplinas'] = self.object.disciplinas.all()
        return initial

    def form_valid(self, form):
        messages.success(self.request, "Curso atualizado com sucesso!")
        return super().form_valid(form)


class CursoDeleteView(DeleteView):
    model = Curso
    template_name = "Cursos/curso_confirm_delete.html"
    success_url = reverse_lazy("curso_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Curso removido com sucesso.")
        return super().delete(request, *args, **kwargs)


# ==========================
# DISCIPLINAS
# ==========================
class DisciplinaListView(ListView):
    model = Disciplina
    template_name = "Cursos/disciplina_list.html"
    context_object_name = "disciplinas"

    def get_queryset(self):
        curso_id = self.kwargs.get('curso_id')
        if curso_id:
            curso = get_object_or_404(Curso, pk=curso_id)
            return curso.disciplinas.all()
        return Disciplina.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curso_id = self.kwargs.get('curso_id')
        if curso_id:
            context['curso'] = get_object_or_404(Curso, pk=curso_id)
            context['curso_id'] = curso_id
        return context

class DisciplinaCreateView(CreateView):
    model = Disciplina
    form_class = DisciplinaForm
    template_name = "Cursos/disciplina_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curso_id = self.kwargs.get("curso_id")
        if curso_id:
            context['curso'] = get_object_or_404(Curso, pk=curso_id)
            context['curso_id'] = curso_id
        return context

    def form_valid(self, form):
        messages.success(self.request, "Disciplina criada com sucesso!")
        return super().form_valid(form)

    def get_success_url(self):
        curso_id = self.kwargs.get("curso_id")
        if curso_id:
            return reverse_lazy("disciplina_list", kwargs={"curso_id": curso_id})
        return reverse_lazy("curso_list")

class DisciplinaUpdateView(UpdateView):
    model = Disciplina
    form_class = DisciplinaForm
    template_name = "Cursos/disciplina_edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Encontrar o curso associado (primeiro curso que contém esta disciplina)
        disciplina = self.get_object()
        cursos_associados = disciplina.cursos.all()
        if cursos_associados.exists():
            context['curso'] = cursos_associados.first()
        return context

    def get_success_url(self):
        disciplina = self.get_object()
        cursos_associados = disciplina.cursos.all()
        if cursos_associados.exists():
            return reverse_lazy("disciplina_list", kwargs={"curso_id": cursos_associados.first().id})
        return reverse_lazy("curso_list")

class DisciplinaDeleteView(DeleteView):
    model = Disciplina
    template_name = "Cursos/disciplina_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        disciplina = self.get_object()
        cursos_associados = disciplina.cursos.all()
        if cursos_associados.exists():
            context['curso'] = cursos_associados.first()
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Disciplina removida com sucesso.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        disciplina = self.get_object()
        cursos_associados = disciplina.cursos.all()
        if cursos_associados.exists():
            return reverse_lazy("disciplina_list", kwargs={"curso_id": cursos_associados.first().id})
        return reverse_lazy("curso_list")