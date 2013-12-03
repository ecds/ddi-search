from django.shortcuts import render

from ddisearch.ddi.forms import SearchForm
from ddisearch.ddi.models import CodeBook

def site_index(request):
    return render(request, 'site_index.html', {'form': SearchForm()})


def search(request):
    form = SearchForm(request.GET)
    context = {'form': form}
    if form.is_valid():
        # generate query here
        keywords = form.cleaned_data['keyword']


        results = CodeBook.objects.filter(fulltext_terms=keywords) \
                    .order_by('-fulltext_score') \
                    .only('title', 'fulltext_score')
        print results.count()
        context.update({'keywords': keywords, 'results': results})

    return render(request, 'ddi/search.html', context)
