# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GeonamesContinent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(unique=True, max_length=2)),
                ('geonames_id', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GeonamesCountry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(unique=True, max_length=2)),
                ('numeric_code', models.IntegerField()),
                ('continent', models.CharField(max_length=2)),
                ('geonames_id', models.IntegerField()),
            ],
            options={
                'verbose_name_plural': 'geonames countries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('geonames_id', models.IntegerField(unique=True)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('country_code', models.CharField(max_length=2, null=True, blank=True)),
                ('feature_code', models.CharField(max_length=10)),
                ('continent_code', models.CharField(max_length=10, null=True, blank=True)),
                ('state_code', models.CharField(max_length=3, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StateCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=2)),
                ('fips', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
