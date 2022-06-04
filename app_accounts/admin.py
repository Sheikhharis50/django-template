from django.contrib import admin
from django.contrib.admin import StackedInline
from django.contrib.auth.admin import (
    UserAdmin as BaseUserAdmin,
    GroupAdmin as BaseGroupAdmin,
)
from .forms import (
    UserAdminCreationForm,
    UserAdminChangeForm,
)
from .models import (
    Group,
    ProxyUser,
    ProxyUserProfile,
)


class UserProfileAdmin(StackedInline):
    model = ProxyUserProfile
    list_display = (
        "gender",
        "contact",
        "dob",
        "website",
    )
    extra = 0


admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    list_display = (
        "id",
        "name",
    )
    ordering = ("id",)


@admin.register(ProxyUser)
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileAdmin]
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = (
        "email",
        "full_name",
        "group_names",
        "is_email_verified",
        "is_active",
        "is_hidden",
        "created_at",
    )
    list_filter = (
        "is_staff",
        "is_active",
        "is_hidden",
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("username", "first_name", "last_name")},
        ),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "is_email_verified", "is_hidden")},
        ),
        ("Group Permissions", {"classes": ("wide",), "fields": ("groups",)}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
    search_fields = ["email"]
    ordering = ("-created_at",)
    filter_horizontal = ()

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("groups")

    def full_name(self, obj):
        return obj.full_name

    def group_names(self, obj):
        return ", ".join([x.name for x in obj.groups.all()])

    def superuser(self, obj):
        return obj.is_superuser

    superuser.short_description = "Superuser"
    superuser.boolean = True
