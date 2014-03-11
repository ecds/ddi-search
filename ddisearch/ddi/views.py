import datetime
from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from urllib import urlencode
from eulexistdb.exceptions import DoesNotExist

from ddisearch.ddi import forms
from ddisearch.ddi.models import CodeBook, Keyword, Topic

def site_index(request):
    'Site index page; currently just displays the search form.'
    # find all documents that are new within some arbitrary window
    # currently using 90 days
    new_since = datetime.date.today() - datetime.timedelta(days=90)
    new_resources = CodeBook.objects \
          .filter(document_version__date__gte=new_since.isoformat()) \
          .only('id', 'title', 'document_version') \
          .order_by('-document_version__date')  # newest first
    # should we limit the list at some point?
    return render(request, 'site_index.html',
        {'form': forms.KeywordSearch(), 'new_resources': new_resources,
        'new_since': new_since})


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
        if 'location' in search_opts and search_opts['location']:
            results = results.filter(location__fulltext_terms=search_opts['location'])

        # date search
        if 'start_date' in search_opts and 'end_date' in search_opts:
            sdate = search_opts['start_date']
            edate = search_opts['end_date']
            # NOTE: needs to handle date format variation (YYYY, YYYY-MM, etc)

            # single date search: start and end date should be the same;
            # using same logic as range to match any dates within that year
            # if only one of start or end is specified, results in an open range
            # i.e. anything after start date or anything before end date
            if sdate is not None:
                # restrict by start date
                # YYYY will be before any date in that year, e.g. "2001" >= "2001-11"
                results = results.filter(time_periods__date__gte=str(sdate))
            if edate is not None:
                # restrict by end date
                # convert to end of year to catch any date variants within that year
                # e.g. 2001-12-31 will always come after 2001-04, etc
                edate = "%s-12-31" % edate
                results = results.filter(time_periods__date__lte=str(edate))

        # To make relevance scores more meaningful, run *all* search terms
        # from any field against the full text and boost fields
        # *IF* we are doing a fultext search (i.e., not a date-only query)
        if form.all_search_terms:
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
        # clear out blank fields
        # (in particular, without this numeric date fields come through as None)
        for k in list(url_args.keys()):
            if url_args[k] is None or url_args[k] == '':
                del url_args[k]
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
            'querytime': [results.object_list.queryTime()],
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


def resource_xml(request, agency, id):
    '''Display the raw DDI XML for a single document; returns a 404
    if no record matching the specified agency and id is found.

    :param agency: agency identifier (from document title statement)
    :param id: id number (from title statement)
    '''
    try:
        res = CodeBook.objects.get(id__val=id, id__agency=agency)
    except DoesNotExist:
        raise Http404

    xml = res.serialize(pretty=True)
    return HttpResponse(xml, mimetype='application/xml')


def browse_terms(request, mode):
    '''Browse list of distinct keywords or topics (depending on the
    specified mode), or browse documents by keyword or topic if a term
    is specified as a request parameter.

    :param mode: keywords or topics
    '''

    fltr = mode.rstrip('s')
    term = request.GET.get(fltr, None)

    if term is not None:
        results = CodeBook.objects.filter(**{mode:term}) \
                    .only('title', 'abstract', 'keywords', 'topics',
                          'authors', 'time_periods', 'id')

        # TODO: re-use sort (w/o relevance) & pagination options from search
        per_page = 10

    else:
        # FIXME: how to sort *after* the distinct?
        if mode == 'keywords':
            results = Keyword.objects.all().distinct().order_by_raw('%(xq_var)s')

        elif mode == 'topics':
            results = Topic.objects.all().distinct().order_by_raw('%(xq_var)s')

        per_page = 50

    # returns a list of string, not xml objects

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

    # counting per item is TOO slow; how to correlate with the terms?
    # counts = []
    # for t in terms.object_list:
    #     counts.append(CodeBook.objects.filter(topics=t).count())
    label = mode.title()
    url_args = {}
    if term:
        label = label.rstrip('s')
        # url params to preserve when jumping to another page
        url_args[fltr] = term

    return render(request, 'ddi/browse_terms.html',
        {'mode': mode, 'label': label, 'term': term, 'results': results,
        'fltr': fltr, 'url_params': urlencode(url_args)})
