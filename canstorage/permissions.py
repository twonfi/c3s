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

from canstorage.models import Can
from canstorage.models import AccessControlList as Acl


class DjangoModelViewEditPermissions(DjangoModelPermissions):
    """Similar to DjangoModelPermissions, but extends to views."""

    def __init__(self):
        self.perms_map["GET"] = ["%(app_label)s.view_%(model_name)s"]


class AccessControlListPermissions(BasePermission):
    """Determine permissions from a can's access control list."""

    METHOD_PERMISSIONS = {
        "GET": Acl.INDEX,
        "HEAD": Acl.INDEX,
        "POST": Acl.WRITE,
        "PUT": Acl.WRITE,
        "PATCH": Acl.WRITE,
        "DELETE": Acl.WRITE,
    }

    # noinspection PyTypeChecker
    def has_object_permission(self, request, view, obj: Can):
        if request.method in self.METHOD_PERMISSIONS:
            return obj.access_control_list.check_permission(
                self.METHOD_PERMISSIONS[request.method], request.user
            )
        return False
