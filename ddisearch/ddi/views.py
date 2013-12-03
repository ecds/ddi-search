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


        results = CodeBook.objects.filter(fulltext_terms=keywords) \
                    .order_by('-fulltext_score') \
                    .only('title', 'fulltext_score')

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
        url_params = urlencode({
            'keyword': keywords.encode('utf-8'),
            'per_page': per_page
        })

        context.update({'keywords': keywords, 'results': results,
            'pages': pages, 'url_params': url_params})

    return render(request, 'ddi/search.html', context)
