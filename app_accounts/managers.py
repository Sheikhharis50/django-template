from django.conf import settings
from django.contrib.auth.models import BaseUserManager

from utils.enums import Roles
from utils.helpers import with_cache


class UserManager(BaseUserManager):
    related_fields = ("groups",)

    def get(self, *args, **kwargs):
        return super().prefetch_related(*self.related_fields).get(*args, **kwargs)

    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    @with_cache(settings.CACHE_FOR_DAY)
    def get_admins(self):
        return self.filter(groups__name=Roles.ADMIN.value).values("id", "email")
