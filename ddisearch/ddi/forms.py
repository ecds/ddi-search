from django import forms

class SearchForm(forms.Form):
    keyword = forms.CharField(required=True,
        help_text='One or more keywords; can include wildcards * and ?, and exact phrases in quotes.')