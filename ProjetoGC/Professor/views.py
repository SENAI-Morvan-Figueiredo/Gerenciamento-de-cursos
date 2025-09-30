from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Import do decorator específico do app login
from Login.decorators import professor_required

@login_required
@professor_required
def dashboard_professor(request):
    return render(request, "templates/Professor.html")
