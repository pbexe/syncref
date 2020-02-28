from django import forms
from .models import ReferenceFile


class ReferenceUpload(forms.Form):
    pdf = forms.FileField()