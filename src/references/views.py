from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from .models import GroupMembership, Group, Reference
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

def index(request):
    if request.user.is_authenticated:
        group_relations = GroupMembership.objects.filter(user=request.user)
        groups = [i.group for i in group_relations]
        return render(request, "references/app.html", {"groups": groups})
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


@login_required
def create_group(request):
    if request.method == "POST":
        name = request.POST["name"]
        description = request.POST["description"]
        group = Group(name=name, description=description, admin=request.user)
        group.save()
        membership = GroupMembership(group=group, user=request.user)
        membership.save()
        return HttpResponse("OK")
    return render(request, "references/create_group.html")