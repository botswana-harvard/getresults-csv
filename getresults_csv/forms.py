from django import forms
from getresults_csv.models import CsvDictionary


class CsvDictionaryForm(forms.ModelForm):

    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('processing_field') and cleaned_data.get('utestid'):
            raise forms.ValidationError(
                'Link the csv field to either a process field or utestid, but not both')

    class Meta:
        model = CsvDictionary
        fields = '__all__'
