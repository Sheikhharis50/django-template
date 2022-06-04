from django.apps import AppConfig as BaseAppConfig
from django.contrib.admin.apps import AdminConfig as BaseAdminConfig
from django.conf import settings


class AdminConfig(BaseAdminConfig):
    default_site = "app.admin.AdminSite"


class AppConfig(BaseAppConfig):
    name = settings.APP_NAME
