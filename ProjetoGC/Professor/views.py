# Professor/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Example: If you have a custom User model or need more user data
# from .models import ProfessorProfile # Assuming you might have a profile model later

@login_required
def professor_home(request):
    # You can fetch data here if needed, e.g., upcoming agenda items, latest classes
    # context = {
    #     'user': request.user,
    #     'upcoming_events': [],
    #     'recent_classes': []
    # }
    return render(request, 'professor/home.html', {'user': request.user})

# You would add other views here for Agenda, Turmas, Diario, etc.
# @login_required
# def professor_agenda(request):
#     return render(request, 'professor/agenda.html')