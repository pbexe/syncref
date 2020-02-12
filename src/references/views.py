from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from .models import GroupMembership, GroupMembership, Reference


def index(request):
    if request.user.is_authenticated:
        return render(request, "references/app.html")
    else:
        return render(request, "references/index.html")


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            user.is_superuser = True 
            user.is_staff = True 
            user.save()
            auth_login(request, user)

            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "references/signup.html", {"form": form})


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return redirect("home")
        else:
            messages.error(request,"Invalid Credentials")
    return render(request, "references/login.html")


def create_group(request):
    if request.method == "POST":
        name = request.POST["name"]
        description = request.POST["description"]
        group = Group(name=name, description=description)
        group.save()
    return render(request, "references/login.html")