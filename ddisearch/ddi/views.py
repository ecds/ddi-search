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
    if form.is_valid():
        # generate query here
        keywords = form.cleaned_data['keyword']
        per_page = form.cleaned_data['per_page']
        sort = form.cleaned_data['sort']

        from ddisearch.ddi.models import patch_codebook
        patch_codebook()

        results = CodeBook.objects \
                    .filter(fulltext_terms=keywords) \
                    .or_filter(fulltext_terms=keywords,
                               boostfields__fulltext_terms=keywords) \
                    .order_by(sort) \
                    .only('title', 'abstract', 'keywords', 'topics',
                          # 'sort_date__min',
                          'dates',
                          # 'start_dates', 'end_dates', 'sort_date', 'dates',
                          'fulltext_score')
        paginator = Paginator(results, per_page, orphans=5)

        print '**** query time results are ?', results.queryTime()
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
        del url_args['per_page']
        rechunk_params = urlencode(url_args)


        context.update({'keywords': keywords, 'results': results,
            'pages': pages, 'url_params': url_params,
            'per_page': int(per_page),
            'rechunk_params': rechunk_params,
            'per_page_choices': forms.AdvancedSearch.PER_PAGE_CHOICES})

    return render(request, 'ddi/search.html', context)
