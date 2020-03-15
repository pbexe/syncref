import json
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.postgres.search import (SearchQuery, SearchRank,
                                            SearchVector)
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from habanero import cn

from .bibparser import bib2py, py2bib
from .dublincore import url2doi
from .forms import ReferenceUpload
from .grobextract import ExtractionError, content_negotiation, extract
from .models import (Group, GroupMembership, Reference, ReferenceField,
                     ReferenceFile, ReferenceType)


@never_cache
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
        groups = [i.group for i in GroupMembership.objects.filter(user=request.user)]
        references = []
        for group in groups:
            references += Reference.objects.filter(group=group)
        return render(request, "references/app.html", {
            "groups": groups,
            "references": references
            })
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
            user.is_active = False
            user.save()
            return HttpResponse("Your accound must be verified by an admin")
    else:
        form = UserCreationForm()
    return render(request, "references/signup.html", {
        "form": form,
        # "groups": [i.group for i in GroupMembership.objects.filter(user=request.user)]
        })


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
            messages.error(request, "Invalid Credentials")
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
        return redirect("view_group", pk=group.pk)
    return render(request, "references/create_group.html",{
        "groups": [i.group for i in GroupMembership.objects.filter(user=request.user)]
    })


@login_required
@never_cache
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
            "group": group,
            "references": references,
            "groups": [i.group for i in GroupMembership.objects.filter(user=request.user)]

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
                                pairs[request.POST[key].casefold()] = request.POST[value]

                                break
            # TODO ensure proper ID TYPE etc
            pairs["ENTRYTYPE"] = request.POST["type"]
            pairs["ID"] = request.POST["name"]
            reference = Reference(name=request.POST["name"],
                                  bibtex_dump=[pairs],
                                  group=group)
            reference.save()
            return redirect("view_group", pk=group.pk)
        else:
            return render(request, "references/add.html", {
                "pk": group.pk,
                "groups": [i.group for i in GroupMembership.objects.filter(user=request.user)],
                "types": ReferenceType.objects.all()
            })
    else:
        raise PermissionDenied


@login_required
def edit_references(request, pk, reference):
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
                                pairs[request.POST[key].casefold()] = request.POST[value]
                                break
                                # Forgive me for the indentation
            pairs["ID"] = request.POST["name"]
            pairs["ENTRYTYPE"] = request.POST["type"]
            reference_object = Reference.objects.get(pk=reference)
            reference_object.name = request.POST["name"]
            reference_object.bibtex_dump = [pairs]
            reference_object.group = group
            reference_object.save()
            return redirect("view_reference", pk=group.pk, reference=reference)
        else:
            return render(request, "references/add.html", {
                "pk": group.pk,
                "groups": [i.group for i in GroupMembership.objects.filter(user=request.user)]

            })
    else:
        raise PermissionDenied


@login_required
def uploadReference(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if GroupMembership.objects.filter(group=group, user=request.user).exists():
        if request.method == 'POST':
            form = ReferenceUpload(request.POST, request.FILES)
            if form.is_valid():
                try:
                    pdf = request.FILES['pdf']
                    info = extract(pdf)
                    try:
                        bibtex = content_negotiation(*info[:2])
                        bibtex_py = bib2py(bibtex)
                        messages.success(request, "PDF successfully parsed")
                    except ExtractionError as e:
                        bibtex = {}
                        bibtex["ID"] = "Unknown"
                        bibtex["ENTRYTYPE"] = "misc"
                        if info[0]:
                            bibtex["title"] = info[0]
                        if info[1]:
                            bibtex["author"] = " and ".join(data[1])
                        bibtex["comment"] = "ERROR: No candidate was found. This is all the data I could extract"
                        bibtex_py = [bibtex]
                        messages.warning(request, "Could not match the PDF with any known papers. The reference has been filled with the extracted data. Expect this to be wrong.")
                    reference = Reference(name=bibtex_py[0]["title"],
                                        bibtex_dump=bibtex_py,
                                        group=group,
                                        fulltext=info[2])
                    reference.save()
                    reference_file = ReferenceFile(pdf=pdf, reference=reference)
                    reference_file.save()
                    return redirect("view_reference", pk=group.pk, reference=reference.pk)
                except ExtractionError as e:
                    messages.error(request, "Error extracting from PDF: " + str(e))
                    return redirect("add", pk)
        else:
            form = ReferenceUpload()
        return render(request, 'references/upload.html', {
            'form': form,
            "groups": [i.group for i in GroupMembership.objects.filter(user=request.user)]

        })
    else:
        raise PermissionDenied


@login_required
def uploadPDFToReference(request, pk, reference):
    group = get_object_or_404(Group, pk=pk)
    if GroupMembership.objects.filter(group=group, user=request.user).exists():
        if request.method == 'POST':
            form = ReferenceUpload(request.POST, request.FILES)
            if form.is_valid():
                reference_file = ReferenceFile(pdf=request.FILES['pdf'],
                                               reference=get_object_or_404(Reference,
                                                                           pk=reference))
                reference_file.save()
                return redirect("view_reference", pk=group.pk, reference=reference)
        else:
            form = ReferenceUpload()
        return render(request, 'references/upload.html', {
            'form': form,
            "groups": [i.group for i in GroupMembership.objects.filter(user=request.user)]

        })
    else:
        raise PermissionDenied


@login_required
def submit_url(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if GroupMembership.objects.filter(group=group, user=request.user).exists():
        if request.method == 'POST':
            url = request.POST["url"]
            try:
                doi = url2doi(url)
                if not doi:
                    messages.error(request, "No DOI was found on the page")
                    return redirect("add", pk=pk)
                bibtex = cn.content_negotiation(ids=doi, format="bibentry")
                entry = bib2py(bibtex)
                reference = Reference(name=entry[0]["title"], bibtex_dump=entry, group=group)
                reference.save()
                messages.success(request, "URL successfully parsed")
                return redirect("view_reference", pk=group.pk, reference=reference.pk)
            except Exception as e:
                messages.error(request, 'There was an error adding the link: ' + str(e))
                return redirect("add", pk=pk)
        else:
            return render(request, "references/url.html", {
                "pk": pk,
                "groups": [i.group for i in GroupMembership.objects.filter(user=request.user)]

            })
    else:
        raise PermissionDenied


@login_required
def add_user_to_group(request, pk):
    # TODO It is never checked if the reference is in the group. This happens
    # for every authentication in this style.
    group = get_object_or_404(Group, pk=pk)
    if GroupMembership.objects.filter(group=group, user=request.user).exists():
        if request.method == 'POST':
            if "user" in request.POST:
                username = request.POST["user"]
                user = get_object_or_404(User, username=username)
                # user = User.objects.get(username=username)
                member = GroupMembership(group=group, user=user)
                member.save()
                return HttpResponse("Added " + username + " to group")
            else:
                return HttpResponse("User does not exist")
        else:
            raise PermissionDenied
    else:
        raise PermissionDenied


@login_required
def delete_reference(request, reference):
    # TODO This is a better way of checking the reference is allower=d to be
    # modified
    reference = get_object_or_404(Reference, pk=reference)
    group = reference.group
    if GroupMembership.objects.filter(group=group, user=request.user).exists():
        reference.delete()
        return HttpResponse("OK")
    else:
        raise PermissionDenied


@login_required
def add_template(request, pk, template):
    group = get_object_or_404(Group, pk=pk)
    if GroupMembership.objects.filter(group=group, user=request.user).exists():
        template = get_object_or_404(ReferenceType, pk=template)
        fields = ReferenceField.objects.filter(referenceType=template)
        numbers = list(range(1,len(fields)+1))
        fields = zip(fields, numbers)
        return render(request, "references/add_template.html", {
            "pk": group.pk,
            "groups": [i.group for i in GroupMembership.objects.filter(user=request.user)],
            "fields": fields,
            "types": ReferenceType.objects.all(),
            "type": template.name
        })
    else:
        raise PermissionDenied


@never_cache
@login_required
def view_references(request, pk, reference):
    group = get_object_or_404(Group, pk=pk)
    if GroupMembership.objects.filter(group=group, user=request.user).exists():
        reference = Reference.objects.get(pk=reference)
        key_pairs = reference.bibtex_dump[0].copy()
        new_key_pairs = {}
        print(key_pairs)
        name = key_pairs["ID"]
        del key_pairs["ID"]
        entrytype = key_pairs["ENTRYTYPE"]
        del key_pairs["ENTRYTYPE"]
        for i, key in enumerate(key_pairs, 1):
            new_key_pairs[key] = (key_pairs[key], i)
        files = ReferenceFile.objects.filter(reference=reference)
        return render(request, "references/view_reference.html", {
            "reference": reference,
            "bibtex_py": new_key_pairs,
            "bibtex": py2bib(reference.bibtex_dump).strip(),
            "files": files,
            "name": name,
            "entrytype": entrytype,
            "groups": [i.group for i in GroupMembership.objects.filter(user=request.user)]

        })
        return HttpResponse(py2bib(reference.bibtex_dump))
    else:
        raise PermissionDenied


def combine(references):
    """Makes sure that the `ID` key in each dictionary is unique

    Arguments:
        references {List} -- List of disctionaries representing BibTeX entries

    Returns:
        List -- The modified list of BibTeX entries
    """
    seen = []
    for reference in references:
        for i, val in enumerate(seen):
            if val[0] == reference["ID"]:
                reference["ID"] = reference["ID"] + "_" + str(val[1])
                seen[i][1] += 1
                break
        else:
            seen.append([reference["ID"], 1])
    return references


@never_cache
@login_required
def export(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if GroupMembership.objects.filter(group=group, user=request.user).exists():
        references = Reference.objects.filter(group=group)
        output = []
        for reference in references:
            output += reference.bibtex_dump
        return HttpResponse(py2bib(combine(output)), content_type='application/bibtex')
    else:
        raise PermissionDenied


def view_404(request):
    return render(request, "references/404.html")


def search_vectors_from_keys(keys, attribute_name):
    vector = None
    for key in keys:
        if vector:
            vector += SearchVector(attribute_name + "__" + key, weight="A")
        else:
            vector = SearchVector(attribute_name + "__" + key, weight="A")
    return vector


@login_required
@never_cache
def search(request):
    if request.method == "POST":
        if "query" in request.POST:
            query = request.POST["query"]
            vector = SearchVector('fulltext', weight="C") \
                + search_vectors_from_keys(
                    settings.DEFAULT_SEARCH_TAGS, "bibtex_dump__0"
                    )
            # vector = SearchVector('fulltext', weight="C") \
            #     + SearchVector('bibtex_dump__0__title', weight="A") \
            #     + SearchVector('bibtex_dump__0__author', weight="A")
            query = SearchQuery(query)
            references = Reference.objects.annotate(
                rank=SearchRank(vector, query))\
                .order_by('-rank')\
                # .filter(rank__gt=0)
            groups = GroupMembership.objects.filter(user=request.user)
            r = []
            for reference in references:
                if reference.group in [group.group for group in groups]:
                    r.append(reference)
            if r:
                return render(request, "references/search_results.html", {
                    "results": r,
                    "groups": [i.group for i in GroupMembership.objects.filter(user=request.user)]

                })
            else:
                return HttpResponse("No results")
        else:
            return HttpResponse("Please submit a query")
    else:
        raise PermissionDenied("Please use POST")
