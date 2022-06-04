from rest_framework import permissions


class IsNotSuperUser(permissions.BasePermission):
    """
    Allow all except Superuser.
    """

    message = "Forbidden."

    def has_permission(self, request, view):
        return not request.user.is_superuser


class OnlyAdmin(permissions.BasePermission):
    """
    Only `admin` can read/write.
    """

    message = "Forbidden."

    def has_permission(self, request, view):
        return (not request.user.is_anonymous) and request.user.is_admin


class OnlyAdminCanWrite(permissions.BasePermission):
    """
    Only `admin` can write.
    """

    message = "Forbidden."

    def has_permission(self, request, view):
        permission = True
        if not request.method in permissions.SAFE_METHODS:
            # Check permissions for write request
            permission = hasattr(request.user, "is_admin") and request.user.is_admin
        return permission


class OnlyAdminCanRead(permissions.BasePermission):
    """
    Only `admin` can read.
    """

    message = "Forbidden."

    def has_permission(self, request, view):
        permission = True
        if request.method in permissions.SAFE_METHODS:
            # Check permissions for read-only request
            permission = request.user.is_admin
        return permission


class OnlyGroup(permissions.BasePermission):
    """
    Only given group can read/write.
    """

    message = "Forbidden."
    permission_group = None

    def __init__(self, permission_group) -> None:
        super().__init__()
        self.permission_group = permission_group

    def __call__(self):
        return self

    def has_permission(self, request, view):
        return (
            not request.user.is_anonymous
        ) and request.user.group_name == self.permission_group
