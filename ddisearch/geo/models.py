from django.db import models


class GeonamesCountry(models.Model):
    '''Minimal country information, based on geonames country info download
    http://download.geonames.org/export/dump/countryInfo.txt'''
    #: country name
    name = models.CharField(max_length=255)
    #: two-letter ISO country code
    code = models.CharField(max_length=2, unique=True)
    #: ISO-numeric code
    numeric_code = models.IntegerField()
    #: two-letter continent code
    continent = models.CharField(max_length=2)
    #: numeric geonames id
    geonames_id = models.IntegerField()

    class Meta:
        verbose_name_plural = 'geonames countries'

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.code)

class GeonamesContinent(models.Model):
    '''Continent names and codes from GeoNames, as listed at
    http://download.geonames.org/export/dump/'''
    #: continent name
    name = models.CharField(max_length=255)
    #: two-letter continent code
    code = models.CharField(max_length=2, unique=True)
    #: geonames id
    geonames_id = models.IntegerField()

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.code)

class Location(models.Model):
    #: name of the location
    name = models.CharField(max_length=255)
    #: numeric genoames id, entered in the XML as geonames:#####
    geonames_id = models.IntegerField(unique=True)
    #: latitude
    latitude = models.FloatField()
    #: longitude
    longitude = models.FloatField()
    #: 2-character country code
    country_code = models.CharField(max_length=2, null=True, blank=True)
    #: type or level of place; see http://www.geonames.org/export/codes.html
    feature_code = models.CharField(max_length=10)
    #: two-letter continent code
    continent_code = models.CharField(max_length=10, null=True, blank=True)
    #: two-digit 'adminCode1' from geonames; corresponds to US state
    #: codes, and should allow for grouping US cities by state
    state_code = models.CharField(max_length=3, null=True, blank=True)

    def __unicode__(self):
        return '%s (%s, %s)' % (self.name, self.country_code, self.continent_code)


class StateCode(models.Model):
    'U.S. State abbreviation and FIPS codes, for generating maps'
    #: state name
    name = models.CharField(max_length=255)
    #: two-letter state abbrevation
    code = models.CharField(max_length=2)
    #: numeric FIPS code
    fips = models.IntegerField()

