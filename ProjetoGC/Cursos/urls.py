from django.urls import path
from .views import (
    CursoListView, CursoCreateView, CursoUpdateView, CursoDeleteView,
    DisciplinaListView, DisciplinaCreateView, DisciplinaUpdateView, DisciplinaDeleteView
)

urlpatterns = [
    # Cursos
    path("cursos/", CursoListView.as_view(), name="curso_list"),
    path("cursos/novo/", CursoCreateView.as_view(), name="curso_create"),
    path("cursos/<int:pk>/editar/", CursoUpdateView.as_view(), name="curso_update"),
    path("cursos/<int:pk>/deletar/", CursoDeleteView.as_view(), name="curso_delete"),

    # Disciplinas
    path("disciplinas/<int:curso_id>/", DisciplinaListView.as_view(), name="disciplina_list"),
    path("disciplinas/nova/", DisciplinaCreateView.as_view(), name="disciplina_create_global"),
    path("disciplinas/<int:pk>/editar/", DisciplinaUpdateView.as_view(), name="disciplina_update"),
    path("disciplinas/<int:pk>/deletar/", DisciplinaDeleteView.as_view(), name="disciplina_delete"),
]