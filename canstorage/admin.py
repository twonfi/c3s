#  Copyright (C) 2026 twonum.org / Celeste.
#
#  This file is part of Celeste's Custom Can Storage (C3s).
#
#  C3s is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your
#  option) any later version.
#
#  C3s is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
#  for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with C3s. If not, see <https://www.gnu.org/licenses/>.

from django.contrib import admin

from canstorage import models


@admin.register(models.AccessControlList)
class AccessControlListAdmin(admin.ModelAdmin):
    fields = (
        "name",
        "users",
        "user_permissions",
        "groups",
        "group_permissions",
        "others_permissions",
    )
    filter_horizontal = ("users", "groups")


@admin.register(models.Can)
class CanAdmin(admin.ModelAdmin):
    fields = ("name", "description", "access_control_list")
    readonly_fields = ("creator", "creation_date")

    def get_fields(self, request, obj=None):
        if obj:  # Already exists
            return self.fields + ("creator", "creation_date")
        return self.fields

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Already exists
            return self.readonly_fields + ("name",)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not obj.creator:  # Creating
            obj.creator = request.user
        super().save_model(request, obj, form, change)


# Do not register in admin.
# noinspection PyUnresolvedReferences
class ObjectAdmin(admin.ModelAdmin):
    fields = ("can", "name")
    readonly_fields = ("creator", "creation_date")
    list_display = ("name", "can")
    list_select_related = ("can",)

    def get_fields(self, request, obj=None):
        if obj:  # Already exists
            return self.fields + ("creator", "creation_date")
        return self.fields

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Already exists
            return self.readonly_fields + ("can", "name")
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not obj.creator:  # Creating
            obj.creator = request.user
        super().save_model(request, obj, form, change)


@admin.register(models.Text)
class TextAdmin(ObjectAdmin):
    fields = ObjectAdmin.fields + ("data",)


@admin.register(models.JSON)
class JSONAdmin(ObjectAdmin):
    fields = ObjectAdmin.fields + ("data",)


@admin.register(models.File)
class FileAdmin(ObjectAdmin):
    fields = ObjectAdmin.fields + (
        "data",
        "content_type",
    )


# @admin.register(models.Image)
# class ImageAdmin(ObjectAdmin):
#     fields = ObjectAdmin.fields + ("data",)
