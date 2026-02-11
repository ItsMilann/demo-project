from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """
    Permission class to check if user is a Super Admin.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_super_admin()


class IsCountryAdminOrSuperAdmin(permissions.BasePermission):
    """
    Permission class to check if user is a Country Admin or Super Admin.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_super_admin() or request.user.is_country_admin())
        )

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated and request.user.is_super_admin():
            return True
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.country == obj.country)
        )


class CanCreateUser(permissions.BasePermission):
    """
    - Super Admin can create users for any country
    - Country Admin can only create users for their assigned country
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if not (request.user.is_super_admin() or request.user.is_country_admin()):
            return False

        if request.method == "POST":
            country = request.data.get("country")

            if request.user.is_super_admin():
                return True

            if request.user.is_country_admin():
                return country == request.user.country

        return True


class CanAlterUser(IsCountryAdminOrSuperAdmin):
    """
    Permission class to check if user is a Country Admin or Super Admin.
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated and request.user.is_super_admin():
            return True
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.country == obj.country)
        )
