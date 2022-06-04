from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions


class InvalidToken(exceptions.AuthenticationFailed):
    default_detail = _("Token is expired or invalid.")
    default_code = "token_expired_or_invalid"


class InvalidUser(exceptions.AuthenticationFailed):
    default_detail = _("Unauthorized User.")
    default_code = "unauthorized_user"
