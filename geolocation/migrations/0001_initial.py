# Generated by Django 4.0.6 on 2022-07-25 15:11

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geoname_id', models.PositiveIntegerField(null=True)),
                ('capital', models.CharField(blank=True, max_length=163)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=2)),
                ('name', models.CharField(blank=True, max_length=25)),
                ('native', models.CharField(blank=True, max_length=25)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='geolocation.location')),
            ],
        ),
        migrations.CreateModel(
            name='GeoLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(null=True)),
                ('ip_type', models.CharField(blank=True, choices=[('ipv4', 'Ipv4'), ('ipv6', 'Ipv6'), ('None', 'Not Provided')], max_length=4)),
                ('continent_code', models.CharField(max_length=2)),
                ('continent_name', models.CharField(max_length=13)),
                ('country_code', models.CharField(max_length=2)),
                ('country_name', models.CharField(max_length=56)),
                ('region_code', models.CharField(blank=True, max_length=2)),
                ('region_name', models.CharField(blank=True, max_length=85)),
                ('city', models.CharField(blank=True, max_length=163)),
                ('postal_code', models.CharField(blank=True, max_length=12)),
                ('coordinates', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('is_eu', models.BooleanField(default=False)),
                ('location', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='geolocation.location')),
            ],
        ),
    ]