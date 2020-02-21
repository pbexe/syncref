from django import forms
from .models import ReferenceFile


class ReferenceUpload(forms.ModelForm):
    class Meta:
        model = ReferenceFile
        fields = ('pdf',)