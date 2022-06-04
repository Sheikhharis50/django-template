from django.contrib.admin import AdminSite as BaseAdminSite
from django.conf import settings


class AdminSite(BaseAdminSite):
    index_title = f"{settings.APP_NAME} Site Administration"
