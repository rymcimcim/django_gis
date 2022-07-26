"""django_gis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from rest_framework.permissions import AllowAny
from rest_framework.routers import SimpleRouter

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from geolocations.views import GeoLocationViewSet
from languages.views import LanguageViewSet
from locations.views import LocationViewSet

router = SimpleRouter()
router.register(r'geolocations', GeoLocationViewSet, basename='geolocations')
router.register(r'languages', LanguageViewSet, basename='languages')
router.register(r'locations', LocationViewSet, basename='locations')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include((router.urls, 'router'), namespace='api')),
    path('api/token/', TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(permission_classes=(AllowAny,)), name='token_refresh'),
]
