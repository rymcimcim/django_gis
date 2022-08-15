import os

from django.contrib.gis.geoip2 import GeoIP2
from django.db import transaction

import requests

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer

from geolocations.models import (
    GeoLocation,
)
from geolocations.serializers import (
    GeoIP2Serializer,
    GeoLocationSerializer,
    IPStackSerializer,
)
from base.utils import is_ip_address
from base.tasks import dump_data_base


IPSTACK_URL = 'http://api.ipstack.com/'


class GeoLocationCreateFactory:
    def _create_from_serializer_payload(self, serializer_class: ModelSerializer, payload: dict) -> Response:
        serializer = serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def _get_geoip2_payload(self, data: str) -> dict:
        g = GeoIP2()
        country = g.country(data)
        city = g.city(data)
        coordinates = g.geos(data)
        payload = {**country, **city, 'coordinates': coordinates}

        ip_addr = is_ip_address(data)
        if ip_addr:
            payload | {'ip':ip_addr[0],'ip_type':ip_addr[1]}

        return payload

    def _create_from_geoip2(self, data: str) -> Response:
        payload = self._get_geoip2_payload(data)
        return self._create_from_serializer_payload(GeoIP2Serializer, payload)
    
    def _create_from_ipstack(self, ip: str) -> Response:
        def get_ipstack_payload(ip: str) -> dict:
            r = requests.get(IPSTACK_URL + ip, params={'access_key': os.environ["IPSTACK_ACCESS_KEY"]})
            payload = r.json()
            if payload.get('success') == 'false':
                payload = self._get_geoip2_payload(ip)

            return payload

        payload = get_ipstack_payload(ip)
        return self._create_from_serializer_payload(IPStackSerializer, payload)

    def create_geolocation(self, request: Request):
        url = request.GET.pop('url', None)
        ip = request.GET.pop('ip', None)
        if url and ip:
            raise ValidationError("Both 'url' and 'ip' parameters provided at the same time are not supported.")
        if url:
            return self._create_from_geoip2(url)
        elif ip:
            return self._create_from_ipstack(ip)
        else:
            raise ValidationError("'url' or 'ip' parameter is required.")

class GeoLocationViewSet(viewsets.ModelViewSet):
    queryset = GeoLocation.objects.all()
    serializer_class = GeoLocationSerializer
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        transaction.on_commit(lambda: dump_data_base.delay())
        return response

    @action(detail=False, methods=['post'])
    def add(self, request) -> Response:
        geoloc_create_factory = GeoLocationCreateFactory()
        return geoloc_create_factory.create_geolocation(request)
