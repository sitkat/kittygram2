from rest_framework import permissions


class IsShelterOwner(permissions.BasePermission):
    """Только владелец приюта может редактировать/удалять."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsShelterStaff(permissions.BasePermission):
    """Владелец или модератор приюта могут управлять сотрудниками."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        shelter = obj if hasattr(obj, 'employees') else obj.shelter
        return shelter.employees.filter(
            user=request.user,
            role__in=('owner', 'moderator'),
        ).exists()
