# Generated by Django 4.1 on 2022-08-10 10:48

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(db_index=True, max_length=2)),
                ('name', models.CharField(max_length=25)),
                ('native', models.CharField(max_length=25)),
            ],
            options={
                'unique_together': {('code', 'name', 'native')},
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('geoname_id', models.PositiveIntegerField(null=True)),
                ('capital', models.CharField(blank=True, max_length=163)),
                ('languages', models.ManyToManyField(blank=True, to='geolocation.language')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GeoLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ip', models.GenericIPAddressField(null=True)),
                ('ip_type', models.CharField(choices=[('ipv4', 'Ipv4'), ('ipv6', 'Ipv6'), ('', 'Not Provided')], default='', max_length=4)),
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
            options={
                'abstract': False,
            },
        ),
    ]
