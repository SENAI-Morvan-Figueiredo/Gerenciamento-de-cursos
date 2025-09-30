from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Import do decorator específico do app login
from Login.decorators import secretaria_required

@login_required
@secretaria_required
def dashboard_professor(request):
    return render(request, "templates/Professor.html")