import json
import re

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Group, GroupMembership, Reference
from .forms import ReferenceUpload


def index(request):
    """View to handle the root directory of the website. If the user is logged
    in, then it is the app home page. If the user is not logged in, then a
    landing page is shown. 
    
    Args:
        request (request): A handle to the request
    
    Returns:
        render: Renders the specified template
    """
    if request.user.is_authenticated:
        group_relations = GroupMembership.objects.filter(user=request.user)
        groups = [i.group for i in group_relations]
        return render(request, "references/app.html", {"groups": groups})
    else:
        return render(request, "references/index.html")


def signup(request):
    """A view to handle the user registration process
    
    Args:
        request (request): A handle to the request
    
    Returns:
        render: Renders the registration form
        redirect: Redirects the user to the home page
    """
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
    """A view to handle the login process
    
    Args:
        request (request): A handle to the request
    
    Returns:
        render: Renders the login form
        redirect: Redirects the user to the home page
    """
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
    """A view to allow the user to create a group
    
    Args:
        request (request): A handle to the request
    
    Returns:
        render: Renders the group creation form
    """
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
    """A view to allow the user to view a specified group
    
    Args:
        request (request): A handle to the request
        pk (int): The promary key of the group
    
    Raises:
        PermissionDenied: Raised when a user who is not a member of the group
                          tries to access the group
    
    Returns:
        render: Renders the group information
    """
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
    """A view to allow the user to add a reference to a group
    
    Args:
        request (request): A handle to the request
        pk (int): The primary key of the group
    
    Raises:
        PermissionDenied: Raised when a user who is not a member of the group
                          tries to access the group
    
    Returns:
        render: The form to allow the addition of a reference
        redirect: Redirects the user to the group home page upon successfull
                  entry of a reference
    """
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
                                # Forgive me for the indentation
            reference = Reference(name=request.POST["name"],
                                  bibtex_dump=pairs,
                                  group=group)
            reference.save()
            return redirect("view_group", pk=group.pk)
        else:
            return render(request, "references/add.html", {
                "pk": group.pk
            })
    else:
        raise PermissionDenied

def uploadReference(request, pk):
    if request.method == 'POST':
        form = ReferenceUpload(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ReferenceUpload()
    return render(request, 'references/upload.html', {
        'form': form
    })