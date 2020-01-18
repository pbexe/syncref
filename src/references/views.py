from django.shortcuts import render

def index(request):
    return render(request, 'references/404.html')