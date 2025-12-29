from django.shortcuts import render

def index(request):
    return render(request, 'web/landing.html')

def login_view(request):
    return render(request, 'web/login.html')
