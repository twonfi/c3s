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

from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import viewsets

from canstorage import models, serializers
from canstorage.permissions import (
    DjangoModelViewEditPermissions,
    AccessControlListPermissions,
)

User = get_user_model()


def _access_denied(request) -> HttpResponse:
    if request.user.is_authenticated:
        r = HttpResponse(
            "You don't have permission to access this can.", status=403
        )
    else:
        # TODO: Return WWW-Authenticate to be HTTP-compliant
        r = HttpResponse(
            "You don't have permission to access this can."
            "  Please authenticate if you have permission.",
            status=401,
        )

    r["Content-Type"] = "text/plain; charset=utf-8"
    r["Allow"] = "GET, HEAD, OPTIONS"
    r["Vary"] = "Accept"
    return r


def can_index(request, can_name: str) -> HttpResponse:
    can = get_object_or_404(models.Can, name=can_name)

    if can.access_control_list.check_permission(
        models.AccessControlList.INDEX, request.user
    ):
        objects = models.Object.objects.filter(can=can)

        preferred_type = request.get_preferred_type(
            [
                "text/plain",
                "text/html",
            ]
        )
        match preferred_type:
            case "text/html":
                context = {
                    "title": f"Index of {can.name}",
                    "favicon": "favicons/can.svg",
                    "can": can,
                    "objects": objects,
                }
                r = render(request, "canstorage/index.html", context)
            case _:  # text/plain or something else
                text = "\n".join(
                    map(lambda x: f"{x.name} [{x.object_type}]", objects)
                )
                r = HttpResponse(
                    text, content_type="text/plain; charset=utf-8"
                )
        r["Allow"] = "GET, HEAD, OPTIONS"
        r["Vary"] = "Accept"
        return r
    else:
        return _access_denied(request)


# noinspection PyUnresolvedReferences
def object_access(request, can_name: str, object_name: str):
    can = get_object_or_404(models.Can, name=can_name)

    if can.access_control_list.check_permission(
        models.AccessControlList.READ, request.user
    ):
        obj = get_object_or_404(models.Object, can=can, name=object_name)

        match obj.object_type:
            case "Text":
                r = HttpResponse(
                    obj.text.data, content_type="text/plain; charset=utf-8"
                )
            case "JSON":
                r = JsonResponse(obj.json.data)
            case "File":
                file_handle = open(obj.file.data.path, "rb")
                r = FileResponse(file_handle)
                r["Content-Type"] = obj.file.content_type
            case _:
                # That wasn't supposed to happen...
                raise Exception

        r["Allow"] = "GET, HEAD, OPTIONS"
        r["Object-Type"] = obj.object_type
        return r
    else:
        return _access_denied(request)


class AccessControlListViewSet(viewsets.ModelViewSet):
    queryset = models.AccessControlList.objects.all()
    serializer_class = serializers.AccessControlListSerializer
    permission_classes = [DjangoModelViewEditPermissions]


class CanViewSet(viewsets.ModelViewSet):
    queryset = models.Can.objects.all()
    serializer_class = serializers.CanSerializer
    permission_classes = [
        DjangoModelViewEditPermissions | AccessControlListPermissions
    ]

    def get_permissions(self):
        if self.action in {
            "list",
            "create",
            "destroy",
        }:
            return [DjangoModelViewEditPermissions()]
        return super().get_permissions()


class ObjectViewSet(viewsets.ReadOnlyModelViewSet):
    # TODO: Implement writing and remove ReadOnly
    serializer_class = serializers.ObjectSerializer
    permission_classes = [
        DjangoModelViewEditPermissions | AccessControlListPermissions
    ]
    lookup_field = "name"

    def get_queryset(self):
        return models.Object.objects.filter(can__pk=self.kwargs["can_pk"])

    def get_permissions(self):
        return super().get_permissions()
