from rest_framework import viewsets

from languages.models import Language
from languages.serializers import LanguageSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
