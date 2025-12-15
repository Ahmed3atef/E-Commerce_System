from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls


admin.site.site_header = "Ecommerce System"

urlpatterns = [
    path('admin/', admin.site.urls),
    
    #auth
    path("api/account/", include("account.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    urlpatterns += debug_toolbar_urls()