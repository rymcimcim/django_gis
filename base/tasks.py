import logging

from django.core.management import CommandError, call_command
from django.core.management.commands import dumpdata

from django_gis.celery import app

logger = logging.getLogger(__name__)


@app.task
def dump_data_base() -> None:

    with open('geolocations/fixtures/geolocations.json', 'w', encoding='utf-8') as file:
        try:
            call_command(dumpdata.Command(), exclude=['contenttypes', 'auth'], format='json', stdout=file)
        except CommandError:
            logger.debug('Connection with primary database failed.')
