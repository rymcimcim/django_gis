from django.db import transaction

from rest_framework import status, viewsets
from rest_framework.response import Response

from geolocations.models import (
    GeoLocation,
    Location
)
from geolocations.serializers import (
    GeoIP2Serializer,
    GeoLocationSerializer,
    IPStackSerializer,
    LocationSerializer
)
from base.tasks import dump_data_base


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class GeoLocationViewSet(viewsets.ModelViewSet):
    queryset = GeoLocation.objects.all()

    def get_serializer(self, *args, **kwargs):
        serializer_class = None
        request = kwargs.pop('request', None)
        try:
            if request.method in ('POST', 'PUT', 'PATCH'):
                if kwargs.get('data').get('is_in_european_union'):
                    serializer_class = GeoIP2Serializer
                else:
                    serializer_class = IPStackSerializer
        except AttributeError:
            serializer_class = GeoLocationSerializer
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(request=request, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, request=request, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        transaction.on_commit(lambda: dump_data_base.delay())
        return response
