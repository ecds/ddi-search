from django import forms

default = {
    'per_page': 10,
    'sort': '-fulltext_score'
}

class KeywordSearch(forms.Form):
    keyword = forms.CharField(required=True,
        help_text='One or more keywords; can include wildcards * and ?, and exact phrases in quotes.')
    per_page = forms.IntegerField(initial=default['per_page'], widget=forms.HiddenInput)


class AdvancedSearch(KeywordSearch):
    PER_PAGE_OPTIONS = (10, 25, 50, 100)
    page_choices = [(d, d) for d in PER_PAGE_OPTIONS]
    per_page = forms.ChoiceField(label='Results per page',
        choices=page_choices, initial=default['per_page'])
    SORT_OPTIONS = ('relevance', 'title', 'date (recent)', 'date (oldest)')
    sort_choices = [(d, d) for d in SORT_OPTIONS]
    sort = forms.ChoiceField(label='Sort by',
        choices=sort_choices, initial=default['sort'])