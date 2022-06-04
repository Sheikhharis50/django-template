from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from django.db import models

from rest_framework import exceptions, serializers, validators
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer as BaseTokenRefreshSerializer,
    TokenObtainPairSerializer as BaseTokenObtainPairSerializer,
)
from rest_framework_simplejwt.exceptions import TokenBackendError


from .models import (
    User,
    Group,
    UserProfile,
)
from app.core.serializers import (
    AppSerializer,
    AppModelSerializer,
)

from utils.enums import Roles, Gender
from utils.helpers import log

RolesMap = {
    Roles.ADMIN: User,
}


class TokenObtainPairSerializer(BaseTokenObtainPairSerializer, AppSerializer):
    """
    Inherit from `TokenObtainPairSerializer` and it will validate
    email and password.
    """

    default_error_messages = {"no_active_account": _("No active account.")}

    def verify_user(self):
        truthy = [
            self.user.is_active,
            self.user.is_email_verified,
            not self.user.is_hidden,
        ]
        group_name = self.user.group_name

        if group_name and group_name != Roles.ADMIN.value:
            try:
                filters = {"is_hidden": False, "user": self.user}
                truthy.append(
                    RolesMap[Roles(group_name)].objects.filter(**filters).exists()
                )
            except Exception as e:
                log(str(e))
        return all(truthy)

    def validate_email(self, email):
        if not email:
            raise serializers.ValidationError("Email is required.")

        user = User.objects.filter(
            models.Q(email=email) | models.Q(username=email)
        ).first()

        if not user:
            raise exceptions.AuthenticationFailed(
                self.default_error_messages.get("no_active_account")
            )

        return user.email

    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.verify_user():
            raise exceptions.AuthenticationFailed(
                self.default_error_messages.get("no_active_account")
            )

        self.user.refresh_token = data.get("refresh")
        self.user.save(update_fields=["refresh_token"])
        return data

    @property
    def errors(self):
        return self.get_errors()


class TokenRefreshSerializer(BaseTokenRefreshSerializer, AppSerializer):
    """
    Inherit from `TokenRefreshSerializer` and touch the database
    before re-issuing a new access token and ensure that the user
    exists and is active.
    """

    default_error_messages = {"no_active_account": _("No active account.")}
    token_error = _("Token is invalid or expired.")

    def validate(self, attrs):
        user = None
        try:
            token_payload = token_backend.decode(attrs["refresh"])
            user = User.objects.get(
                pk=token_payload["user_id"],
                is_active=True,
                is_superuser=False,
                is_email_verified=True,
                is_hidden=False,
            )
        except TokenBackendError:
            raise exceptions.NotAcceptable(self.token_error, "invalid_or_expired_token")
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                self.default_error_messages.get("no_active_account")
            )

        if user.refresh_token != attrs.get("refresh"):
            raise exceptions.NotAcceptable(self.token_error, "invalid_or_expired_token")

        tokens = super().validate(attrs)
        user.refresh_token = tokens.get("refresh")
        user.save(update_fields=["refresh_token"])
        return tokens

    @property
    def errors(self):
        return self.get_errors()


class UserProfileSerializer(AppModelSerializer):
    gender = serializers.ChoiceField(choices=Gender.choices)
    contact = serializers.CharField(allow_blank=True)
    dob = serializers.DateField(allow_null=True)
    website = serializers.CharField(allow_blank=True)

    class Meta:
        model = UserProfile
        fields = ["gender", "contact", "dob", "website"]

    def create(self, validated_data):
        user_id = self.context.get("user_id")
        data = dict(
            gender=validated_data.get("gender"),
            contact=validated_data.get("contact"),
            dob=validated_data.get("dob"),
            website=validated_data.get("website"),
            user_id=user_id,
        )
        return UserProfile.objects.create(**data)


class UserViewSerializer(AppModelSerializer):
    """
    UserViewSerializer serializing the User Model
    """

    class Meta:
        model = User
        fields = [
            "id",
            "title",
            "first_name",
            "last_name",
            "full_name",
            "username",
            "email",
        ]


class UserDetailViewSerializer(UserViewSerializer):
    """
    UserDetailViewSerializer serializing the User Model
    """

    profile = UserProfileSerializer(read_only=True)

    class Meta(UserViewSerializer.Meta):
        model = User
        fields = UserViewSerializer.Meta.fields + [
            "profile",
            "is_email_verified",
            "is_active",
        ]


class UserCreateSerializer(AppModelSerializer):
    """
    UserCreateSerializer serializing the User Model
    """

    queryset = User.objects.all()
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(
        required=True,
        validators=[validators.UniqueValidator(queryset=queryset)],
    )
    username = serializers.CharField(
        required=False,
        validators=[validators.UniqueValidator(queryset=queryset)],
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={"input_type": "password"},
        validators=[validate_password] if not settings.DEBUG else [],
        help_text="In case of Patient you don't need to add password.",
    )
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = [
            "title",
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
            "profile",
        ]

    def validate_email(self, email):
        return email.lower()

    def validate_username(self, username):
        return username.lower()

    def create(self, validated_data):
        is_active = self.context.get("is_active", True)
        password = validated_data.get("password")
        profile_data = validated_data.get("profile")
        data = dict(
            username=validated_data.get("username"),
            email=validated_data.get("email"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            is_active=is_active,
        )
        if settings.DEBUG:
            data["is_email_verified"] = True

        # bypassing password for patient.
        if not is_active:
            # set password for patient to be {username}1234
            password = "{}1234".format(validated_data.get("username"))
        elif not password:
            # if is_active is True and password is not provided, raise error.
            raise exceptions.ValidationError({"password": "This field is required."})

        # creating user
        user = User(**data)
        user.set_password(password)
        user.save()

        # storing user profile
        profile_data = UserProfileSerializer(
            data=profile_data,
            context={"user_id": user.id},
        )
        profile_data.is_valid(raise_exception=True)
        profile_data.save()

        return user


class UserUpdateSerizlizer(AppModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
    is_active = serializers.BooleanField(
        initial=True,
        help_text="In case of Patient Is active will be ignored.",
    )
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = [
            "title",
            "first_name",
            "last_name",
            "username",
            "is_active",
            "profile",
        ]

    def validate_username(self, value):
        if self.instance and User.objects.exclude(pk=self.instance.pk).filter(
            username=value
        ):
            raise serializers.ValidationError("This field must be unique.")
        return value.lower()

    def update(self, instance, validated_data):
        instance = self.set_validated_data(
            instance,
            validated_data,
            excludes=["profile", "is_active"],
            save=False,
        )
        instance.is_active = self.context.get(
            "is_active", validated_data.get("is_active")
        )
        profile_data = UserProfileSerializer(
            instance=instance.profile,
            data=validated_data.get("profile"),
            partial=True,
        )
        profile_data.is_valid(raise_exception=True)
        profile_data.save()
        instance.save()
        return instance


class UserActivateSerizlizer(AppModelSerializer):
    class Meta:
        model = User
        fields = [
            "is_active",
        ]


class GroupSerializer(AppModelSerializer):
    """
    GroupSerializer serializing the Group Model
    """

    class Meta:
        model = Group
        fields = ["name"]


class WhoAmISerializer(AppModelSerializer):
    """
    WhoAmISerializer serializing is used to Serialize the User and
    get data which is required for frontend.
    """

    groups = serializers.SerializerMethodField()

    def get_groups(self, obj):
        groups = GroupSerializer(obj.groups.all(), many=True).data
        try:
            for group in groups:
                role = Roles(group.get("name"))
                if role == Roles.ADMIN:
                    group[f"{role.value}_id"] = obj.id
                    continue
                group[f"{role.value}_id"] = (
                    RolesMap[role]
                    .objects.filter(
                        user__id=obj.id,
                        is_hidden=False,
                    )
                    .first()
                    .pk
                )

        except Exception as e:
            log(str(e))
        return groups

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "groups",
            "is_active",
        ]


class ChangePasswordSerializer(AppModelSerializer):

    error_mg = "Invalid Password."
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        validators=[validate_password] if not settings.DEBUG else [],
    )

    class Meta:
        model = User
        fields = [
            "old_password",
            "new_password",
        ]

    def update(self, instance: User, validated_data):
        if not instance.check_password(validated_data.get("old_password")):
            raise exceptions.ValidationError(dict(detail=self.error_mg))

        instance.set_password(validated_data.get("new_password"))
        instance.save()

        return instance


class ForgotPasswordSerializer(AppModelSerializer):
    email = serializers.EmailField(
        write_only=True,
        required=True,
    )

    def validate_email(self, email: str):
        email = email.lower()
        user = self.Meta.model.objects.filter(
            email=email,
            is_email_verified=True,
            is_active=True,
        ).first()
        if not user:
            raise exceptions.ValidationError("User not found.")
        return user

    class Meta:
        model = User
        fields = ["email"]


class ResetPasswordSerializer(AppSerializer):
    token = serializers.CharField(
        write_only=True,
        required=True,
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
    )
