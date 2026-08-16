from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.permissions import IsAdminUser, AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="TeuEmpregoAqui API",
        default_version='v1',
        description="We connect you with real, verified job opportunities across the EU — powered by official government data sources only.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="mdsadiqulislam446@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(IsAdminUser,) if not settings.DEBUG else (AllowAny,),
)

handler404 = 'apps.core.views.custom_404'
handler500 = 'apps.core.views.custom_500'

urlpatterns = [
    path("admin/", admin.site.urls),
    
    path('api/v1/', include([
        path('candidate/', include('apps.candidate.urls')),
        path('crosswalk/', include('apps.crosswalk.urls')),
        path('francetravail/', include('apps.francetravail.urls')),
        path('legal/', include('apps.legal.urls')),
        path('content/', include('apps.contents.urls')),
        path('analytics/', include('apps.analytics.urls')),
        path('education/', include('apps.education.urls')),
    ])),
]

if settings.DEBUG:
    urlpatterns += [
        path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)