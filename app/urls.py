from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf.urls.static import static
from django.conf import settings
from django.urls import include, path
from django.views.generic.base import RedirectView
from rest_framework.documentation import include_docs_urls
import debug_toolbar

urlpatterns = [
    # adminsite
    path("api/admin/", admin.site.urls),
    # third-party tools
    path("api/__debug__/", include(debug_toolbar.urls)),
    path(
        "api/v1/docs/",
        include_docs_urls(
            title=settings.APP_NAME,
            public=settings.DEBUG,
            schema_url=settings.ENDPOINT,
        ),
    ),
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("img/favicon.ico")),
    ),
    # custom apps
    path("api/v1/", include("app_accounts.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # restframework session authentication
    urlpatterns.append(
        path("api/auth/", include("rest_framework.urls")),
    )
