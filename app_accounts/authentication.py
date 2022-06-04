from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings

from utils.helpers import log

from app_accounts.exceptions import (
    InvalidToken,
    InvalidUser,
)


class SafeJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                log(e)

        raise InvalidToken()

    def get_user(self, validated_token):

        try:
            return super().get_user(validated_token)
        except Exception as e:
            log(e)

        raise InvalidUser()
