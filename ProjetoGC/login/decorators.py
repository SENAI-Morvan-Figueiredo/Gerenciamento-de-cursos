from django.shortcuts import redirect
from functools import wraps

def aluno_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.tipo == "aluno":
            return view_func(request, *args, **kwargs)
        return redirect("login")
    return wrapper

def professor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.tipo == "professor":
            return view_func(request, *args, **kwargs)
        return redirect("login")
    return wrapper

def secretaria_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.tipo == "secretaria":
            return view_func(request, *args, **kwargs)
        return redirect("login")
    return wrapper
