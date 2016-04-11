# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.core.management import call_command


def load_fixture(apps, schema_editor):
    'Load geographic coutry, continent, and state codes from a fixture'
    call_command('loaddata', 'geographic_codes', app_label='geo')

def unload_fixture_data(apps, schema_editor):
    'Remove geographic country, continent, and state codes.'
    GeonamesCountry = apps.get_model('geo', 'GeonamesCountry')
    GeonamesContinent = apps.get_model('geo', 'GeonamesContinent')
    StateCode = apps.get_model('geo', 'StateCode')

    GeonamesCountry.objects.all().delete()
    GeonamesContinent.objects.all().delete()
    StateCode.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture,
                reverse_code=unload_fixture_data, atomic=False)
    ]
