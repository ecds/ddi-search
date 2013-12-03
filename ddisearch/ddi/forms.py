from django import forms

default_per_page = 10

class KeywordSearch(forms.Form):
    keyword = forms.CharField(required=True,
        help_text='One or more keywords; can include wildcards * and ?, and exact phrases in quotes.')
    per_page = forms.IntegerField(initial=default_per_page, widget=forms.HiddenInput)


class AdvancedSearch(KeywordSearch):
    PER_PAGE_CHOICES = (10, 25, 50, 100)
    page_choices = [(d, d) for d in PER_PAGE_CHOICES]
    per_page = forms.ChoiceField(label='Results per page',
        choices=page_choices, initial=default_per_page)