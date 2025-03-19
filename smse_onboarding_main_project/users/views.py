from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Faculty

# Create your views here.

@login_required
def profile(request):
    try:
        faculty = Faculty.objects.get(user=request.user)
        return render(request, 'users/profile.html', {'faculty': faculty})
    except Faculty.DoesNotExist:
        messages.error(request, 'Faculty profile not found.')
        return redirect('login')
