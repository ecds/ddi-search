from django.contrib import admin
from ddisearch.geo.models import Location, GeonamesCountry,  GeonamesContinent

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'geonames_id', 'country_code', 'feature_code',
                    'latitude', 'longitude')
    list_filter = ('country_code', 'feature_code')
    search_fields = ('name', 'geonames_id', 'country_code')


class GeonamesCountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'continent')
    list_filter = ('continent',)
    search_fields = ('name', 'code', 'continent')


class GeonamesContinentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'geonames_id')
    search_fields = ('name', 'code', 'geonames_id')


admin.site.register(Location, LocationAdmin)
admin.site.register(GeonamesCountry, GeonamesCountryAdmin)
admin.site.register(GeonamesContinent, GeonamesContinentAdmin)
