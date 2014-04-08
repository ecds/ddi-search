from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from ddisearch.ddi.models import CodeBook


class CodeBookSitemap(Sitemap):

    def items(self):
        return CodeBook.objects.only('id', 'last_modified')

    def location(self, obj):
        return reverse('ddi:resource',
                   kwargs={'agency': obj.id.agency, 'id': obj.id.val})

    def lastmod(self, obj):
        return obj.last_modified


class ContentSitemap(Sitemap):
    # changefreq = 'monthly'    # this content should change more rarely
    # NOTE: could set priority for resources and make this lower
    # default_priority = 0.4


    def items(self):
        # special case pages - index, static html site pages
        return [
            reverse('site-index'),
            reverse('ddi:browse-terms', kwargs={'mode': 'topics'})
        ]

    def location(self, item):
        return item


# dictionary of sitemap objects for use with sitemap views
sitemap_cfg = {
    'dataresources': CodeBookSitemap,
    'sitecontent': ContentSitemap
}