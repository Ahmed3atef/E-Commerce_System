from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from debug_toolbar.toolbar import debug_toolbar_urls


admin.site.site_header = "Ecommerce System"

urlpatterns = [
    path('admin/', admin.site.urls),
    
    #auth
    path("api/auth/", include("account.auth.urls")),
    path("api/account/", include("account.urls")),
    path("api/store/", include("store.urls")),
    path("api/product/", include("product.urls")),
    
    
]

if settings.DEBUG:
    urlpatterns.extend([
        # Swagger / OpenAPI
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ])
    urlpatterns.extend(static( settings.MEDIA_URL,document_root=settings.MEDIA_ROOT))
    urlpatterns.extend(debug_toolbar_urls())