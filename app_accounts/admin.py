from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import (
    ProxyUser,
    ProxyUserProfile,
)


class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "group",
        "superuser",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("username", "first_name", "last_name")},
        ),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active")},
        ),
        ("Group Permissions", {"classes": ("wide",), "fields": ("groups",)}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = ()

    def group(self, obj):
        return obj.groups.first()

    def superuser(self, obj):
        return obj.is_superuser

    superuser.short_description = "Superuser"
    superuser.boolean = True


admin.site.register(ProxyUser, UserAdmin)
admin.site.register(ProxyUserProfile)
