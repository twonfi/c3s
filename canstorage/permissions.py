#  Copyright (C) 2026 twonum.org / Celeste.
#
#  This file is part of Celeste's Custom Can Storage (C3s).
#
#  C3s is free software: you can redistribute it and/or modify it under
#  the terms of the GNU Affero General Public License as published by the
#  Free Software Foundation, either version 3 of the License, or (at your
#  option) any later version.
#
#  C3s is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public
#  License for more details.
#
#  You should have received a copy of the GNU Affero General Public
#  License along with C3s. If not, see <https://www.gnu.org/licenses/>.

from rest_framework.permissions import DjangoModelPermissions, BasePermission

from canstorage.models import Can, Object
from canstorage.models import AccessControlList as Acl


class DjangoModelViewEditPermissions(DjangoModelPermissions):
    """Similar to DjangoModelPermissions, but extends to views."""

    def __init__(self):
        self.perms_map["GET"] = ["%(app_label)s.view_%(model_name)s"]


class AccessControlListPermissions(BasePermission):
    """Determine permissions from a can's access control list."""

    METHOD_PERMISSIONS = {
        "GET": Acl.READ,
        "HEAD": Acl.READ,
        "POST": Acl.WRITE,
        "PUT": Acl.WRITE,
        "PATCH": Acl.WRITE,
        "DELETE": Acl.WRITE,
    }

    # noinspection PyTypeChecker
    def has_object_permission(self, request, view, obj, perm=None):
        if request.method == "OPTIONS":
            return True

        if not perm:
            perm = self.METHOD_PERMISSIONS[request.method]

        tp = type(obj)
        if tp is Can:
            acl = obj.access_control_list
        elif tp is Acl:
            acl = obj
        elif isinstance(obj, Object):
            acl = obj.can.access_control_list
        else:
            raise AssertionError(
                "obj is not Can, nor AccessControlList, nor Object"
            )

        if request.method in self.METHOD_PERMISSIONS:
            return acl.check_permission(perm, request.user)
        return False

    def has_permission(self, request, view):
        # Prevent circular imports
        from canstorage.views import CanViewSet, ObjectViewSet

        if request.method == "OPTIONS":
            return True

        tp = type(view)
        if tp is CanViewSet:
            if view.kwargs:
                try:
                    acl = Can.objects.get(
                        pk=view.kwargs["pk"]
                    ).access_control_list
                except Can.DoesNotExist:
                    return request.method in {"GET", "HEAD"}
                else:
                    return self.has_object_permission(request, view, acl)
            else:
                return False
        elif tp is ObjectViewSet:
            perm = None

            # noinspection PyUnresolvedReferences
            if view.action == "list" and request.method in [
                "GET",
                "HEAD",
            ]:
                perm = Acl.INDEX

            try:
                acl = Can.objects.get(
                    pk=view.kwargs["can_pk"]
                ).access_control_list
            except Can.DoesNotExist:
                return request.method in {"GET", "HEAD"}
            else:
                return self.has_object_permission(request, view, acl, perm)
        else:
            raise AssertionError("view is not CanViewSet or ObjectViewSet")
