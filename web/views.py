from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile

def index(request):
    return render(request, 'web/landing.html')

@login_required
def dashboard(request):
    return render(request, 'web/dashboard.html')

@login_required
def profile(request):
    return render(request, 'web/profile.html')
