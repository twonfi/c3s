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

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from rest_framework import serializers

from canstorage import models

User = get_user_model()


class AccessControlListSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all()
    )
    groups = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all()
    )

    class Meta:
        model = models.AccessControlList
        fields = (
            "id",
            "name",
            "users",
            "user_permissions",
            "groups",
            "group_permissions",
            "others_permissions",
        )


class CanSerializer(serializers.HyperlinkedModelSerializer):
    access = serializers.SerializerMethodField(read_only=True)
    index = serializers.SerializerMethodField(read_only=True)
    text_index = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Can
        fields = (
            "name",
            "description",
            "access_control_list",
            "access",
            "index",
            "text_index",
        )

    def get_fields(self):
        fields = super().get_fields()
        if self.instance:
            fields["name"].read_only = True
        return fields

    def get_access(self, obj: models.Can) -> int:
        request: HttpRequest | None = self.context.get("request")
        if request is None:
            user = None
        else:
            user = request.user
        return obj.access_control_list.get_permissions(user)[0]

    def get_text_index(self, obj: models.Can) -> str:
        # noinspection PyTypeChecker
        request: HttpRequest = self.context.get("request")
        return request.build_absolute_uri(obj.get_absolute_url())


class CanObjectIndexSerializer(serializers.HyperlinkedModelSerializer): ...
