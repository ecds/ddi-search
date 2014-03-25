from django.shortcuts import render, get_object_or_404

from ddisearch.ddi.models import CodeBook
from ddisearch.geo.models import Location


def browse(request):
    geo_id = request.GET.get('geonames_id', None)
    context = {}
    if geo_id is not None:
        place = get_object_or_404(Location, geonames_id=geo_id)
        # TODO: get places underneath
        # find documents
        resources = CodeBook.objects\
                            .filter(geo_coverage__id='geonames:%d' % place.geonames_id)

        context.update({'place': place, 'resources': resources})
    else:
        places = Location.objects.filter(feature_code='CONT')
        context['places'] = places
    return render(request, 'geo/browse_places.html', context)
