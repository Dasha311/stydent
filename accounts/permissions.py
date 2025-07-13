from rest_framework.permissions import BasePermission

class IsMentor(BasePermission):
    """Allows access only to users with the mentor role."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in {'mentor', 'teacher'}
        )

class IsStudent(BasePermission):
    """Allows access only to users with the student role."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'student')


class IsAdmin(BasePermission):
    """Allows access only to admin users."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )