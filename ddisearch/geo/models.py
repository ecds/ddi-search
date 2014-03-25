from django.db import models

# Create your models here.


class GeonamesCountry(models.Model):
    'Minimal country information, based on geonames country info download'
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=2, unique=True)
    continent = models.CharField(max_length=2)
    # TODO: may want foreign key relation to continent instead...

    class Meta:
        verbose_name_plural = 'geonames countries'

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.code)

class GeonamesContinent(models.Model):
    'Continent names and codes from GeoNames'
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=2, unique=True)
    geonames_id = models.IntegerField()

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.code)

class Location(models.Model):
    name = models.CharField(max_length=255)
    geonames_id = models.IntegerField(unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    country_code = models.CharField(max_length=10, null=True, blank=True)  # 2 ?

    # type/level of place ?
    feature_code = models.CharField(max_length=10)
    # continent code ?

    # ?? FIXME; maybe use relations instead of country code ?
    # geonames_country = models.ForeignKey(GeonamesCountry, to_field='code')

