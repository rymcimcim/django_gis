import os
import socket

from django.contrib.gis.geoip2 import GeoIP2
from django.core.exceptions import ValidationError
from django.db import transaction

import requests

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.request import Request

from geolocations.models import (
    GeoLocation,
)
from geolocations.serializers import (
    GeoIP2Serializer,
    GeoIP2WithIPSerializer,
    GeoLocationSerializer,
    IPStackSerializer,
)
from base.utils import is_ip_address
from base.tasks import dump_data_base


IPSTACK_URL = 'http://api.ipstack.com/'


class GeoLocationCreateFactory:
    def create(self, data: dict) -> Response:
        serializer = GeoLocationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _get_geoip2_payload(self, data: str) -> dict:
        g = GeoIP2()
        try:
            payload = g.city(data)
        except ValidationError as exc:
            raise serializers.ValidationError(detail=exc.message, code=exc.code) from exc
        except socket.gaierror as exc:
            raise serializers.ValidationError(detail=exc.strerror, code='invalid')

        ip_addr = is_ip_address(data)
        if ip_addr:
            payload.update({'ip':data,'ip_type':ip_addr})
        return payload

    def _create_from_geoip2(self, data: str) -> Response:
        payload = self._get_geoip2_payload(data)
        geoip2_serializer = GeoIP2Serializer(data=payload)
        geoip2_serializer.is_valid(raise_exception=True)
        return self.create(data=geoip2_serializer.validated_data)
    
    def _create_from_ipstack(self, ip: str) -> Response:
        def get_ipstack_payload_and_serializer_class(ip: str) -> dict:
            r = requests.get(IPSTACK_URL + ip, params={'access_key': os.environ["IPSTACK_ACCESS_KEY"]})
            payload = r.json()
            serializer_class = IPStackSerializer
            if payload.get('success') == 'false':
                payload = self._get_geoip2_payload(ip)
                serializer_class = GeoIP2WithIPSerializer

            return payload, serializer_class

        payload, serializer_class = get_ipstack_payload_and_serializer_class(ip)
        ipstack_serializer = serializer_class(data=payload)
        ipstack_serializer.is_valid(raise_exception=True)
        return self.create(data=ipstack_serializer.validated_data)

    def create_geolocation(self, request: Request) -> Response:
        url = request.GET.get('url', None)
        ip = request.GET.get('ip', None)
        if url and ip:
            raise serializers.ValidationError("Both 'url' and 'ip' parameters provided at the same time are not supported.")
        if url:
            return self._create_from_geoip2(url)
        elif ip:
            return self._create_from_ipstack(ip)
        else:
            raise serializers.ValidationError("'url' or 'ip' parameter is required.")


class GeoLocationViewSet(viewsets.ModelViewSet):
    queryset = GeoLocation.objects.all()
    serializer_class = GeoLocationSerializer
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        transaction.on_commit(lambda: dump_data_base.delay())
        return response

    @action(detail=False, methods=['get'])
    def add(self, request) -> Response:
        geoloc_create_factory = GeoLocationCreateFactory()
        return geoloc_create_factory.create_geolocation(request)
