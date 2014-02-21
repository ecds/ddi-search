from django.shortcuts import render
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from urllib import urlencode
from eulexistdb.exceptions import DoesNotExist

from ddisearch.ddi import forms
from ddisearch.ddi.models import CodeBook

def site_index(request):
    'Site index page; currently just displays the search form.'
    return render(request, 'site_index.html', {'form': forms.KeywordSearch()})


def search(request):
    '''Search all available DDI content by keyword, title, summary, or source
    with sorting by relevance (default), title, or date.'''
    form = forms.KeywordSearch(request.GET)
    context = {'form': form}

    # if the form is valid, process and generate search results;
    # if not, fall through and display the form with validation errors
    if form.is_valid():
        search_opts = form.cleaned_data
        per_page = form.cleaned_data['per_page']
        sort = form.cleaned_data['sort']

        # build query based on search terms here
        results = CodeBook.objects.all()

        if 'keyword' in search_opts and search_opts['keyword']:
            keywords = search_opts['keyword']
            results = results.filter(fulltext_terms=keywords)
                             # .or_filter(fulltext_terms=keywords,
                             #            boostfields__fulltext_terms=keywords,
                             #            highlight=False    # disable highlighting in search results list
                             #            )

        if 'title' in search_opts and search_opts['title']:
            results = results.filter(title__fulltext_terms=search_opts['title'])
        if 'summary' in search_opts and search_opts['summary']:
            results = results.filter(abstract__fulltext_terms=search_opts['summary'])
        if 'source' in search_opts and search_opts['source']:
            results = results.filter(authors__fulltext_terms=search_opts['source'])

        # To make relevance scores more meaningful, run *all* search terms
        # from any field against the full text and boost fields
        results = results.or_filter(fulltext_terms=form.all_search_terms,
                                    boostfields__fulltext_terms=form.all_search_terms,
                                    highlight=False    # disable highlighting in search results list
                                    )
        # FIXME: redundancy in boost fields seems to generate very high relevance scores
        # see if we can avoid repeating filters (e.g. search by title then search again in boost fields)

        # only return fields needed to generate search results
        results = results.only('title', 'abstract', 'keywords', 'topics',
                               'authors', 'time_periods', 'fulltext_score',
                               'id')

        # simple sort mapping
        sort_map = {'title': 'title', 'relevance': '-fulltext_score'}
        if sort in sort_map:
            results = results.order_by(sort_map[sort])
        elif sort.startswith('date'):
            # either date sorting requires a raw xpath to sort on earlist date
            # check which type to determine if results should be ascending or note
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

        url_args = form.cleaned_data
        url_params = urlencode(url_args)
        # url params for changing chunk size
        partial_args = url_args.copy()
        del partial_args['per_page']
        rechunk_params = urlencode(partial_args)
        # url params for changing sort
        partial_args = url_args.copy()
        del partial_args['sort']
        sort_params = urlencode(partial_args)

        context.update({'keywords': search_opts.get('keywords', ''),
            'results': results,
            'url_params': url_params,
            'per_page': int(per_page),
            'rechunk_params': rechunk_params,
            'per_page_options': forms.KeywordSearch.PER_PAGE_OPTIONS,
            'sort': sort,
            'sort_params': sort_params,
            'sort_options': forms.KeywordSearch.SORT_OPTIONS})

    # if form is not valid but *nothing* was submitted (i.e., new search)
    # don't consider the form to be invalid, but just display it
    elif not request.GET:
        # re-init as new form without any validation errors
        context['form'] = forms.KeywordSearch()

    return render(request, 'ddi/search.html', context)

def resource(request, agency, id):
    '''Display a single DDI document with all relevant details.  Uses
    id number and agency to identify a single document; returns a 404
    if no record matching the specified agency and id is found.

    :param agency: agency identifier (from document title statement)
    :param id: id number (from title statement)
    '''
    try:
        res = CodeBook.objects.get(id__val=id, id__agency=agency)
    except DoesNotExist:
        raise Http404

    return render(request, 'ddi/resource.html', {'resource': res})

