from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from urllib import urlencode

from eulcommon.searchutil import pages_to_show

from ddisearch.ddi import forms
from ddisearch.ddi.models import CodeBook

def site_index(request):
    return render(request, 'site_index.html', {'form': forms.KeywordSearch()})


def search(request):
    form = forms.AdvancedSearch(request.GET)
    context = {'form': form}

    required_terms = ['keyword', 'per_page', 'sort']
    # if the form is not valid and *none* of the required terms are present,
    # assume this is a new search and display an empty search form
    if not form.is_valid() and not any(d in request.GET for d in required_terms):
        # re-init for display, without any 'required field' error messages
        context['form'] = forms.AdvancedSearch()

    elif form.is_valid():
        # generate query here
        keywords = form.cleaned_data['keyword']
        per_page = form.cleaned_data['per_page']
        sort = form.cleaned_data['sort']


        results = CodeBook.objects \
                    .filter(fulltext_terms=keywords) \
                    .or_filter(fulltext_terms=keywords,
                               boostfields__fulltext_terms=keywords) \
                    .order_by(sort) \
                    .only('title', 'abstract', 'keywords', 'topics',
                          'dates', 'fulltext_score')

        if sort == 'title':
            results = results.order_by(sort)
        elif sort == 'relevance':
            results = results.order_by('-fulltext_score')
        elif sort.startswith('date'):
            if sort == 'date (recent)':
                asc = False
            elif sort == 'date (oldest)':
                asc = True
            results = results.order_by_raw(CodeBook.sort_date_xpath, ascending=asc)

        paginator = Paginator(results, per_page, orphans=5)

        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        # If page request (9999) is out of range, deliver last page of results.
        try:
            results = paginator.page(page)
        except (EmptyPage, InvalidPage):
            page = paginator.num_pages
            results = paginator.page(paginator.num_pages)

        pages = pages_to_show(paginator, page)

        # NOTE: can we use cleaned_data directly here?
        url_args = form.cleaned_data
        url_params = urlencode(url_args)
        # url params for changing chunk size
        partial_args = url_args.copy()
        del partial_args['per_page']
        rechunk_params = urlencode(partial_args)
        partial_args = url_args.copy()
        del partial_args['sort']
        sort_params = urlencode(partial_args)

        context.update({'keywords': keywords, 'results': results,
            'pages': pages, 'url_params': url_params,
            'per_page': int(per_page),
            'rechunk_params': rechunk_params,
            'per_page_options': forms.AdvancedSearch.PER_PAGE_OPTIONS,
            'sort': sort,
            'sort_params': sort_params,
            'sort_options': forms.AdvancedSearch.SORT_OPTIONS})

    return render(request, 'ddi/search.html', context)
