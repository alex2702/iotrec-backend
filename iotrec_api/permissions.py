from pprint import pprint

from rest_framework import permissions


class IsSignupOrIsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        # allow user signups
        if request.method == 'POST':
            return True

        # otherwise, only allow if authenticated
        return request.user and request.user.is_authenticated
