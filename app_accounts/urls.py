from django.urls import path

from .views import (
    # Auth
    TokenRefreshView,
    TokenObtainPairView,
    WhoAmIView,
    UserView,
    UserActivateView,
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView,
)

urlpatterns = [
    # Auth
    path("token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("whoami", WhoAmIView.as_view()),
    path("forgot-password", ForgotPasswordView.as_view()),
    path("reset-password", ResetPasswordView.as_view()),
    path("user/<uuid:pk>/", UserView.as_view()),
    path("user/<uuid:pk>/active", UserActivateView.as_view()),
    path("user/<uuid:pk>/change-password", ChangePasswordView.as_view()),
]
