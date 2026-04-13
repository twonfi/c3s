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
import re
import secrets
from pathlib import Path
from mimetypes import guess_type

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

User = get_user_model()

OBJECT_NAME_REGEX = re.compile(
    r"^[A-Za-z0-9._-]+(?:/(?!\.+(?:/|$))([A-Za-z0-9._-]+))*$"
)
CAN_NAME_REGEX = re.compile(r"^[A-Za-z0-9-][A-Za-z0-9._-]*$")


def validate_object_name(value: str) -> None:
    msg = "Field may only contain A-Z, 0-9, ., _, -, and well-formed paths, and cannot be an underscore."

    # Easter egg for path traversal
    # (obviously not secure; the later checks actually defend from ../)
    if value.startswith("../"):
        raise ValidationError(
            "You're trying to commit path traversal? Get lost."
        )

    if value == "_":
        raise ValidationError("Name cannot be an underscore.")

    # Simple regex match for allowed characters and well-formed paths
    if not OBJECT_NAME_REGEX.fullmatch(value):
        raise ValidationError(msg)

    # More complex match to defend from path traversal
    random_string = secrets.token_hex(128)
    fake_path = Path(f"/c/fakepath/{random_string}").resolve()
    if not (fake_path / value).resolve().is_relative_to(fake_path):
        raise ValidationError(msg)


def validate_can_name(value: str) -> None:
    if value[0] in {".", "_"}:
        raise ValidationError("Name cannot start with a dot or underscore.")

    if value.endswith(".txt"):
        raise ValidationError("Name cannot end in .txt.")

    if value in {
        "accounts",
        "admin",
        "api",
        "cans",
        "c3s",
        "favicon.ico",
        "media",
        "static",
    }:
        raise ValidationError(
            'Name cannot be a reserved word ("accounts", "admin", "api", "cans", "c3s", "favicon.ico", "media", "static").'
        )

    if not CAN_NAME_REGEX.fullmatch(value):
        raise ValidationError(
            "Name may only contain A-Z, a-z, 0-9, ., _, -, and must not start with a dot or underscore."
        )


class AccessControlList(models.Model):
    """An access control list (ACL) to control access to cans.

    C3s ACLs aren't true ACLs by definition; they are closer to UNIX
    permissions, defining permissions for all users and groups.

    ACLs are defined as separate objects for reusability, allowing for
    an ACL to be used for multiple cans.

    There are three permission levels:

    * Read, Index, Write

      - Retrieve objects
      - List all objects
      - Write to objects

    * Read, Index

      - Retrieve objects
      - List all objects

    * Read

      - Retrieve objects (only with its name)

    Permissions can be applied to entire groups of:

    * Users
    * Groups
    * Everyone else

    Permissions are applied in the order:

    1. Users
    2. Groups
    3. Others

    If users have less access than groups, the user permissions will
    take precedence (the group's permissions aren't applied).
    """

    READ = 4
    WRITE = 2
    INDEX = 1
    NONE = 0
    READ_INDEX = READ + INDEX
    READ_INDEX_WRITE = READ + INDEX + WRITE
    ACCESS_CHOICES = {
        READ_INDEX_WRITE: "Read, index, write",
        READ_INDEX: "Read, index",
        READ: "Read only",
        NONE: "No access",
    }

    name = models.CharField(max_length=32)

    users = models.ManyToManyField(User, blank=True)
    user_permissions = models.PositiveSmallIntegerField(
        choices=ACCESS_CHOICES, default=NONE
    )

    groups = models.ManyToManyField(Group, blank=True)
    group_permissions = models.PositiveSmallIntegerField(
        choices=ACCESS_CHOICES, default=NONE
    )

    others_permissions = models.PositiveSmallIntegerField(
        choices=ACCESS_CHOICES, default=NONE
    )

    def __str__(self) -> str:
        return self.name

    def get_permissions(self, user: User = None) -> tuple[int, int]:
        """Get the permissions ``user`` has.

        :param user: The user attempting to perform the action. If None,
        use others permissions.
        :type user: User
        :return: A tuple. The first item is the access value the user
        has. The second item is an integer from 1 to 3, specifying
        whether user (1), group (2), or others (3) permissions are used.
        :rtype: tuple[int, int]
        """
        if user is None:
            return self.others_permissions, 3
        elif self.users.filter(pk=user.pk).exists():
            return self.user_permissions, 1
        elif self.groups.filter(user__pk=user.pk):
            return self.group_permissions, 2
        else:
            return self.others_permissions, 3

    def check_permission(self, action: int, user: User = None) -> bool:
        """Check if ``user`` is allowed to perform ``action``.

        :param user: The user attempting to perform the action. If None,
        use others permissions.
        :type user: User
        :param action: The action the user is performing. The action
        should be ``self.READ``, ``self.INDEX``, or ``self.WRITE``.
        :type action: int
        :return: Whether the user may perform the action.
        :rtype: bool
        """
        # Users must be authenticated to write
        if action == self.WRITE and (
            user is None or not user.is_authenticated
        ):
            return False
        perm = self.get_permissions(user)[0]
        return bool(perm & action)


class Can(models.Model):
    """A "can", a container for files and other C3s objects.

    Cans are similar to "buckets" in other storage systems and group
    objects together.  Cans are intended to be in a foreign key
    relationship (not a many-to-many); an object should only be in one
    can.
    """

    name = models.CharField(
        primary_key=True,
        max_length=64,
        help_text='A unique, permanent name for the can. May contain A-Z, a-z, 0-9, ., _, -. Must not start with a dot or underscore, or be "accounts", "admin", "api", "cans", "c3s", "favicon.ico", "media", or "static". Cannot be changed after creation.',
        validators=[validate_can_name],
    )
    description = models.TextField(
        help_text="A note for the can. The description is shown to anyone with read access to the can.",
        null=True,
        blank=True,
    )

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    creation_date = models.DateTimeField(auto_now_add=True)

    access_control_list = models.ForeignKey(
        AccessControlList, on_delete=models.PROTECT
    )

    _name_at_creation = models.CharField(
        max_length=64, null=True, blank=True, editable=False
    )

    def save(self, *args, **kwargs) -> None:
        if not hasattr(self, "__name_at_creation"):
            self._name_at_creation = self.name
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        if (
            not self._state.adding  # Updating
            and self.name != self._name_at_creation
        ):
            raise ValidationError("Name cannot be changed after creation.")

    def get_absolute_url(self) -> str:
        return reverse("canstorage:can_index", kwargs={"can_name": self.name})


class Object(models.Model):
    """A base class for other object types."""

    can = models.ForeignKey(
        Can,
        on_delete=models.CASCADE,
        help_text="The parent can of the object. Cannot be changed after creation.",
    )
    name = models.CharField(
        max_length=255,
        help_text="A unique name for the object. Must be unique across all objects in the can. May contain A-Z, a-z, 0-9, ., _, -, and well-formed paths, and cannot start with an underscore. Cannot be changed after creation.",
        validators=[validate_object_name],
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    creation_date = models.DateTimeField(auto_now_add=True)

    object_type = models.CharField(max_length=20)
    object_type_verbose = models.CharField(max_length=20)
    object_type_verbose_plural = models.CharField(max_length=20)

    _can_at_creation = models.ForeignKey(
        Can,
        on_delete=models.CASCADE,
        related_name="_can_at_creation",
        null=True,
        editable=False,
    )
    _name_at_creation = models.CharField(
        max_length=255, null=True, blank=True, editable=False
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["can", "name"], name="unique_can_name"
            )
        ]

    def __str__(self) -> str:
        return f"/{self.can.name}/{self.name}"

    def save(self, *args, **kwargs) -> None:
        # HACK: Approach to get a specific name from an Object QuerySet
        self.object_type = self.__class__.__name__
        self.object_type_verbose = self._meta.verbose_name
        self.object_type_verbose_plural = self._meta.verbose_name_plural

        if hasattr(self, "can") and not hasattr(self, "__name_at_creation"):
            self._can_at_creation = self.can
            self._name_at_creation = self.name

        super().save(*args, **kwargs)

    def clean(self) -> None:
        if (
            not self._state.adding  # Updating
            and (
                self._can_at_creation != self.can
                or self._name_at_creation != self.name
            )
        ):
            raise ValidationError(
                "Can or name cannot be changed after creation."
            )

    def get_object_type_verbose(self):
        return self.object_type_verbose

    def get_absolute_url(self) -> str:
        return reverse(
            "canstorage:can_object",
            kwargs={"can_name": self.can.name, "object_name": self.name},
        )


class _ObjectMeta:
    default_permissions = ()


class Text(Object):
    data = models.TextField(null=True, blank=True)

    class Meta(_ObjectMeta):
        pass


class JSON(Object):
    data = models.JSONField(null=True, blank=True)

    class Meta(_ObjectMeta):
        verbose_name = "JSON"
        verbose_name_plural = "JSONs"


# noinspection PyUnusedLocal
def _get_file_upload_path(instance, filename) -> str:
    return f"{instance.can.name}/{instance.name}"


class File(Object):
    """A file object, which stores an arbitary file."""

    data = models.FileField(upload_to=_get_file_upload_path)
    content_type = models.CharField(
        max_length=64,
        help_text="Content/MIME type of the file. Inferred from file extension of object name by default.",
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.content_type:
            filename = (Path("/fakepath") / self.name).name
            self.content_type = guess_type(filename)[0]
            if not self.content_type:
                self.content_type = "application/octet-stream"

        super().save(*args, **kwargs)

    class Meta(_ObjectMeta):
        pass


# TODO: Optimized image field with automatic conversion
# class Image(Object):
#     """An optimized image object."""
#
#     data = models.ImageField(upload_to=_get_file_upload_path)
