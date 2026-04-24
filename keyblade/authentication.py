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
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from keyblade import models


class KeyAuthentication(authentication.BaseAuthentication):
    AUTHENTICATION_FAILED = AuthenticationFailed(
        "The key used is either invalid, expired, or revoked."
    )

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        private_key = auth_header.removeprefix("Bearer ")
        key_id = private_key.split("--", 1)[0]

        try:
            key = models.Key.objects.get(id=key_id)
        except models.Key.DoesNotExist:
            raise self.AUTHENTICATION_FAILED

        if key.check_key(private_key)[1]:
            return key.user, key
        else:
            raise self.AUTHENTICATION_FAILED

    def authenticate_header(self, request):
        return "Bearer"
