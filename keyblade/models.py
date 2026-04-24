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
import string
from hashlib import sha512
from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

User = get_user_model()


class Key(models.Model):
    """A key for a user."""

    KEY_CHARS = string.ascii_lowercase + string.digits

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.CharField(max_length=36, editable=False, primary_key=True)

    creation_date = models.DateTimeField(auto_now_add=True)

    expiration_date = models.DateField(null=True, blank=True)
    revoked = models.BooleanField(default=False)

    comment = models.CharField(max_length=255, null=True, blank=True)

    key_hash = models.CharField(max_length=255, editable=False)
    # Used to prevent "un-revoking" keys
    _revoked = models.BooleanField(default=False, editable=False)

    def __str__(self) -> str:
        return self.id

    def generate_key(self) -> tuple[str, str]:
        """Generate and set a secret key.

        An ID (public part) is automatically generated if it is None.

        self.save() must be called manually.

        :return: A tuple containing the public ID and the private key.
        :rtype: tuple[str, str]
        """
        if not self.id:
            self.id = "c3s-1-" + get_random_string(32, self.KEY_CHARS)

        private_key = self.id + "--" + get_random_string(64, self.KEY_CHARS)
        self.key_hash = sha512(private_key.encode()).hexdigest()

        return self.id, private_key

    def check_key(self, private_key: str = None) -> tuple[bool, bool | None]:
        """Check the status of the key and, optionally, its private key.

        :param private_key: The private key. If None, skip checking.
        :type private_key: str
        :return: A tuple. The first item is whether the key is valid.
            The second item is whether the key is valid AND the private key
            is correct, or None if private_key is None.
        :rtype: tuple[bool, bool | None]
        """
        if (
            self.revoked
            or (self.expiration_date and self.expiration_date < date.today())
        ):
            return False, False

        if not private_key:
            return True, None

        key_hash = sha512(private_key.encode()).hexdigest()
        if self.key_hash == key_hash:
            return True, True
        else:
            return True, False

    def clean(self) -> None:
        if not self.revoked and self._revoked:
            raise ValidationError("Key revocation is permanent."
                                  " Once a key is revoked,"
                                  " it cannot be undone.")

    def save(self, *args, **kwargs):
        if not self.key_hash:
            self.generate_key()

        if self.revoked:
            self._revoked = True

        super().save(*args, **kwargs)
