from django.conf import settings
from rest_framework import status
from rest_framework.request import Request
from rest_framework_simplejwt.views import (
    TokenRefreshView as BaseTokenRefreshView,
    TokenObtainPairView as BaseTokenObtainPairView,
)

from .serializers import (
    TokenRefreshSerializer,
    TokenObtainPairSerializer,
    WhoAmISerializer,
    UserViewSerializer,
    UserUpdateSerizlizer,
    UserActivateSerizlizer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)
from .models import (
    User,
)

from app.core.response import APIResponse
from app.core.views import (
    AppView,
    AppDetailView,
)
from app.core.functions import call_send_mail
from utils.helpers import create_token, log, verify_token


class TokenObtainPairView(BaseTokenObtainPairView):
    """
    Obtain Pair token generator view.
    """

    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        res = super().post(request, *args, **kwargs)
        return APIResponse(res.data)


class TokenRefreshView(BaseTokenRefreshView):
    """
    Refresh token generator view.
    """

    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        res = super().post(request, *args, **kwargs)
        return APIResponse(res.data)


class WhoAmIView(AppDetailView):
    """
    Check who is login.
    """

    model = User
    serializer_view_class = WhoAmISerializer
    http_method_names = ["get"]

    def get_object(self):
        return self.request.user

    def get(self, request):
        return super().get(request, None)


class UserView(AppDetailView):
    """
    Update and Retrieve `user` information.
    """

    model = User
    serializer_update_class = UserUpdateSerizlizer
    serializer_view_class = UserViewSerializer
    related_many_fields = ("groups",)
    http_method_names = ["get", "put"]

    def get_queryset(self):
        return self.model.objects.prefetch_related(*self.related_many_fields).filter(
            is_superuser=False,
            is_staff=False,
        )


class UserActivateView(AppDetailView):
    """
    Activate and Deactivate `user`.
    """

    model = User
    serializer_partial_update_class = UserActivateSerizlizer
    http_method_names = ["patch"]
    filters = {}
    return_data = False


class ChangePasswordView(AppDetailView):
    """
    Change password of given `user`.
    """

    model = User
    serializer_update_class = ChangePasswordSerializer
    http_method_names = ["put"]
    filters = {}
    return_data = False


class ForgotPasswordView(AppView):
    """
    Forgot password of given `user`.
    """

    model = User
    permission_classes = []
    serializer_create_class = ForgotPasswordSerializer
    http_method_names = ["post"]

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get("email")
            reset_token = create_token(
                text=user.email,
                expires_delta=settings.SIMPLE_JWT.get("RESET_TOKEN_LIFETIME"),
            )
            user.reset_token = reset_token
            user.save(update_fields=["reset_token"])
            call_send_mail(
                subject="Reset Password",
                from_=settings.EMAIL_FROM,
                to_=[user.email],
                template="emails/reset_password.html",
                template_kwargs={
                    "link": f"{settings.FRONTEND_ENDPOINT}/auth/reset-password?token={reset_token}",
                    "lifetime": f"{settings.SIMPLE_JWT.get('RESET_TOKEN_LIFETIME').days} days",
                },
            )
            return APIResponse(detail="Password reset email sent.")
        return APIResponse(
            serializer.get_errors(),
            status=status.HTTP_400_BAD_REQUEST,
        )


class ResetPasswordView(AppView):
    """
    Reset password of given `user`.
    """

    model = User
    permission_classes = []
    serializer_create_class = ResetPasswordSerializer
    http_method_names = ["post"]

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        error_msg = ""

        try:
            serializer.is_valid(raise_exception=True)
            token = serializer.validated_data.get("token")
            new_password = serializer.validated_data.get("new_password")
            email = verify_token(token)
            user: User = self.model.objects.filter(
                email=email,
                is_email_verified=True,
                is_active=True,
            ).first()

            if not user or user.reset_token != token:
                raise Exception("Token is invalid or expired.")

            if user.check_password(new_password):
                raise Exception("Please use another password.")

            user.set_password(new_password)
            user.reset_token = None
            user.save()

            call_send_mail(
                subject="Reset Password Successfully",
                from_=settings.EMAIL_FROM,
                to_=[email],
                template="emails/reset_password_success.html",
                template_kwargs={},
            )

            return APIResponse(detail="Password reset Successfully.")
        except Exception as e:
            error_msg = str(e)
            log(e)

        return APIResponse(
            serializer.get_errors(error_msg=error_msg),
            status=status.HTTP_400_BAD_REQUEST,
        )
