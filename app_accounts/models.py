from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group
from .managers import UserManager
import uuid


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    username = models.CharField(
        verbose_name="username", max_length=255, unique=True, null=True, blank=True
    )
    first_name = models.CharField(
        verbose_name="first_name", max_length=255, null=True, blank=True
    )
    last_name = models.CharField(
        verbose_name="last_name", max_length=255, null=True, blank=True
    )
    is_active = models.BooleanField(verbose_name="Active", default=True)
    is_staff = models.BooleanField(verbose_name="Staff", default=False)
    created_at = models.DateTimeField(verbose_name="created_at", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="updated_at", auto_now=True)
    groups = models.ManyToManyField(Group, related_name="users", blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Email & Password are required by default.

    class Meta:
        db_table = "user"
        verbose_name = "User"

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    @property
    def group(self):
        return self.groups.first()


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        verbose_name="user",
        db_column="user_id",
        to=User,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    contact = models.CharField(
        verbose_name="contact no", max_length=255, null=True, blank=True
    )
    dob = models.DateField(verbose_name="date of birth", null=True, blank=True)
    website = models.CharField(
        verbose_name="website", max_length=255, null=True, blank=True
    )

    class Meta:
        db_table = "user_profile"

    def __str__(self):
        return self.user.email


class ProxyUser(User):
    class Meta:
        app_label = "auth"
        proxy = True
        verbose_name = "User"
        verbose_name_plural = "Users"


class ProxyUserProfile(UserProfile):
    pass

    class Meta:
        app_label = "auth"
        proxy = True
        verbose_name = "UserProfile"
        verbose_name_plural = "UserProfiles"
