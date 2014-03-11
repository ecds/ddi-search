from django import forms


class TelephoneInput(forms.TextInput):
    'HTML5 telephone input (prompt for numeric entry)'
    input_type = 'tel'

class SearchOptions(forms.Form):
    # base form with common options for search and browse result pages
    PER_PAGE_OPTIONS = (10, 25, 50, 100)
    page_choices = [(d, d) for d in PER_PAGE_OPTIONS]
    per_page = forms.ChoiceField(label='Results per page',
        choices=page_choices, initial=10)
    SORT_OPTIONS = ['title', 'date (recent)', 'date (oldest)']
    sort_choices = [(d, d) for d in SORT_OPTIONS]
    sort = forms.ChoiceField(label='Sort by',
        choices=sort_choices, initial='title')

class KeywordSearch(SearchOptions):
    keyword = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control'}),
        help_text='One or more keywords; can include wildcards * and ?, and exact phrases in quotes.')

    # inherit per-page options and input
    # extend sort options to include relevance
    SORT_OPTIONS = ['relevance'] + SearchOptions.SORT_OPTIONS
    sort_choices = [(d, d) for d in SORT_OPTIONS]
    sort = forms.ChoiceField(label='Sort by',
        choices=sort_choices, initial='relevance')

    title = forms.CharField(required=False,
        help_text='Search by title (keywords or phrase)',
        widget=forms.TextInput(attrs={'placeholder':'Search by title', 'class': 'form-control'}))
    summary = forms.CharField(required=False,
        help_text='Search by summary (keywords or phrase)',
        widget=forms.TextInput(attrs={'placeholder':'Search by summary', 'class': 'form-control'}))
    source = forms.CharField(required=False,
        help_text='Search by source organization or principial investigator (keywords or phrase)',
        widget=forms.TextInput(attrs={'placeholder':'Search by source', 'class': 'form-control'}))
    location = forms.CharField(required=False,
        help_text='Search by geographic location, including nation, country, or economic entity',
        widget=forms.TextInput(attrs={'placeholder':'Search by location', 'class': 'form-control'}))

    # NOTE: could use min_value and max_value here, if we have reasonable values
    # default widget is number input; we can switch to text input if helpful
    # this will nned to be a tel input to allow for devices to display the number pad automatically
    # also would be good to add the class form-control to the <input> element
    start_date = forms.IntegerField(required=False,
        help_text=''''Search by start year of time period covered by data;
        use with end date to specify a range or single year''',
        widget=TelephoneInput(attrs={'class': 'form-control', 'placeholder': 'Start year'}))
    end_date = forms.IntegerField(required=False,
        help_text='Search by end date; use with start date to specify a range or single year',
        widget=TelephoneInput(attrs={'class': 'form-control', 'placeholder': 'End year'}))

    _adv_fields = ['title', 'summary', 'source', 'location']

    search_fields = ['keyword', 'start_date', 'end_date'] + _adv_fields
    # fields that can contain search term; at least one of these is required
    # for validation; all combined generate a list of all search terms

    @property
    def advanced_fields(self):
        'fields that are considered part of the "advanced" search'
        return [self[f] for f in self._adv_fields]

    def clean(self):
        'custom validation to ensure at least one search field is populated'
        cleaned_data = super(KeywordSearch, self).clean()
        # any one search term is sufficient, but at least one is required
        if not any([cleaned_data.get(f, None) for f in self.search_fields]):
            raise forms.ValidationError('You must enter search terms for at least one of %s or %s' % \
                                        (', '.join(self.search_fields[:-1]),
                                         self.search_fields[-1]))
        return cleaned_data

    @property
    def all_search_terms(self):
        'string of all search terms present in any search fields'
        try:
            cleaned_data = self.clean()
            return ' '.join([cleaned_data.get(f) for f in self.search_fields
                             if f in cleaned_data and cleaned_data[f]])
        except:
            # if form is not valid, then there are no search terms
            return ''

