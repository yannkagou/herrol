from django import forms
from .models import ImportedFile, Report

class ImportedFileForm(forms.ModelForm):
    class Meta:
        model = ImportedFile
        fields = ['file']

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['name', 'description']
