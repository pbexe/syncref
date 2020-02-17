from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from .models import GroupMembership, Group, Reference
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
import re
import json

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


@login_required
def view_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if GroupMembership.objects.filter(group=group, user=request.user).exists():
        # Get all references to do with the group
        references = Reference.objects.filter(group=group)
        return render(request, "references/group.html", {
            "group":group,
            "references": references
        })
    else:
        raise PermissionDenied


@login_required
def add(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if GroupMembership.objects.filter(group=group, user=request.user).exists():
        if request.method == 'POST':
            pairs = {}
            for key in request.POST:
                if "key" in key:
                    key_number = re.findall(r"[0-9]*$", key)[0]
                    for value in request.POST:
                        if "value" in value:
                            val_number = re.findall(r"[0-9]*$", value)[0]
                            if val_number == key_number:
                                pairs[request.POST[key]] = request.POST[value]
                                break
            reference = Reference(name=request.POST["name"], bibtex_dump=pairs, group=group)
            reference.save()
            return redirect("view_group", pk=group.pk)
        else:
            return render(request, "references/add.html", {
                "pk": group.pk
            })
    else:
        raise PermissionDenied