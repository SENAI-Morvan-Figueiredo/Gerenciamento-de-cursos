from django.urls import path
from .views import (
    CursoListView, CursoCreateView, CursoUpdateView, CursoDeleteView,
    DisciplinaListView, DisciplinaCreateView, DisciplinaUpdateView, DisciplinaDeleteView,
    adicionar_disciplina_curso, remover_disciplina_curso
)

urlpatterns = [
    # Cursos
    path("", CursoListView.as_view(), name="curso_list"),
    path("cursos/novo/", CursoCreateView.as_view(), name="curso_create"),
    path("cursos/<int:pk>/editar/", CursoUpdateView.as_view(), name="curso_update"),
    path("cursos/<int:pk>/deletar/", CursoDeleteView.as_view(), name="curso_delete"),

    # Disciplinas
    path("disciplinas/<int:curso_id>/", DisciplinaListView.as_view(), name="disciplina_list"),
    path("disciplinas/<int:curso_id>/nova/", DisciplinaCreateView.as_view(), name="disciplina_create"),
    path("disciplinas/<int:pk>/editar/", DisciplinaUpdateView.as_view(), name="disciplina_update"),
    path("disciplinas/<int:pk>/deletar/", DisciplinaDeleteView.as_view(), name="disciplina_delete"),
    path("disciplinas/nova/", DisciplinaCreateView.as_view(), name="disciplina_create_global"),
    
    # Novas URLs para gerenciar disciplinas do curso
    path("disciplinas/<int:curso_id>/adicionar/<int:disciplina_id>/", adicionar_disciplina_curso, name="adicionar_disciplina_curso"),
    path("disciplinas/<int:curso_id>/remover/<int:disciplina_id>/", remover_disciplina_curso, name="remover_disciplina_curso"),
]