from django.db import models
from django.utils.translation import gettext_lazy as _
from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def to_dict(cls):
        """
        Returns a dictionary representation of the enum.
        """
        return {item.name: item.value for item in cls}

    @classmethod
    def keys(cls):
        """
        Returns a list of all the enum keys.
        """
        return cls._member_names_

    @classmethod
    def values(cls):
        """
        Returns a list of all the enum values.
        """
        return list(cls._value2member_map_)


class BaseTextChoices(Enum):
    @classmethod
    def single_choices(cls):
        """
        Returns a dictionary representation of the enum.
        """
        return [choice[0] for choice in cls.choices]


class Roles(Enum):
    ADMIN = "admin"


class Gender(models.TextChoices):
    MALE = "male", _("Male")
    FEMALE = "female", _("Female")
    OTHER = "other", _("Other")


class NotificationTypes(Enum):
    pass
