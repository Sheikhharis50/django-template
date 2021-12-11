from django.contrib import admin
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import include, path
import debug_toolbar

urlpatterns = [
    # default
    path("admin/", admin.site.urls),
    # packages
    path("__debug__/", include(debug_toolbar.urls)),
    path("api/v1/auth/", include("rest_framework.urls")),
    path("api/v1/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # custom
    path("api/v1/", include("app_accounts.urls")),
]
