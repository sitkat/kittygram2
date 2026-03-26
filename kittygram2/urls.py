from rest_framework import permissions, routers

from django.contrib import admin
from django.urls import include, path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from cats.views import (
    AchievementViewSet, CatViewSet, ShelterEmployeeViewSet,
    ShelterViewSet, UserViewSet,
)

schema_view = get_schema_view(
    openapi.Info(
        title='Kittygram API',
        default_version='v1',
        description='API приютов и котиков Kittygram',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
router.register('cats', CatViewSet)
router.register('users', UserViewSet)
router.register('achievements', AchievementViewSet)
router.register('shelters', ShelterViewSet)
router.register(
    r'shelters/(?P<shelter_pk>\d+)/staff',
    ShelterEmployeeViewSet,
    basename='shelter-staff',
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
]
