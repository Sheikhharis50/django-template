from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group
import uuid

from .managers import UserManager
from utils.enums import (
    Gender,
    Roles,
)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(verbose_name="Email Address", max_length=255, unique=True)
    username = models.CharField(
        verbose_name="Username", max_length=255, unique=True, null=True, blank=True
    )
    first_name = models.CharField(
        verbose_name="First Name", max_length=255, null=True, blank=True
    )
    last_name = models.CharField(
        verbose_name="Last Name", max_length=255, null=True, blank=True
    )
    title = models.CharField(
        verbose_name="Title", max_length=50, null=True, blank=True, default=""
    )
    reset_token = models.TextField(
        verbose_name="Reset Token",
        max_length=1000,
        null=True,
        blank=True,
    )
    refresh_token = models.TextField(
        verbose_name="Refresh Token",
        max_length=1000,
        null=True,
        blank=True,
    )
    groups = models.ManyToManyField(Group, related_name="users", blank=True)
    is_email_verified = models.BooleanField(
        verbose_name="Email Verified", default=False
    )
    is_active = models.BooleanField(verbose_name="Active", default=True)
    is_staff = models.BooleanField(verbose_name="Staff", default=False)
    is_hidden = models.BooleanField(verbose_name="Hidden", default=False)
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Email & Password are required by default.

    class Meta:
        db_table = "user"
        verbose_name = "User"
        ordering = ["-created_at"]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        _name = "{} {} {}".format(self.title, self.first_name, self.last_name)
        return _name.strip()

    @property
    def short_name(self):
        return self.email

    @property
    def group(self):
        groups = self.groups.all()
        if len(groups):
            return groups[0]
        return None

    @property
    def group_name(self):
        group = self.group
        if group:
            return group.name
        return None

    @property
    def is_admin(self):
        return self.group_name == Roles.ADMIN.value


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        to="app_accounts.User",
        verbose_name="user",
        db_column="user_id",
        related_name="profile",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )
    gender = models.CharField(
        verbose_name="Gender",
        max_length=100,
        choices=Gender.choices,
        null=True,
        blank=True,
    )
    contact = models.CharField(
        verbose_name="Contact No", max_length=255, null=True, blank=True
    )
    dob = models.DateField(verbose_name="Date of birth", null=True, blank=True)
    website = models.CharField(
        verbose_name="Website", max_length=255, null=True, blank=True
    )

    class Meta:
        verbose_name = "User Profile"
        db_table = "user_profile"

    def __str__(self):
        return self.user.email


class ProxyUser(User):
    """
    ProxyUser is just a proxy of `app_accounts.User`
    which is used to show Custom User under auth app.
    """

    class Meta:
        app_label = "auth"
        proxy = True
        verbose_name = "User"
        verbose_name_plural = "Users"


class ProxyUserProfile(UserProfile):
    """
    ProxyUserProfile is just a proxy of `app_accounts.UserProfile`
    which is used to show UserProfile under auth app.
    """

    class Meta:
        app_label = "auth"
        proxy = True
        verbose_name = "UserProfile"
        verbose_name_plural = "UserProfiles"
