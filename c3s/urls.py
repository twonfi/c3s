"""URL config for C3s."""
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

from django.contrib import admin
from django.urls import path, re_path, include
from allauth.account.decorators import secure_admin_login
from rest_framework_nested import routers

from canstorage.views import (
    AccessControlListViewSet,
    CanViewSet,
    ObjectViewSet,
)
from canstorage.routers import CanRouter

admin.autodiscover()
admin.site.login = secure_admin_login(admin.site.login)

admin.site.site_header = "C3s management"
admin.site.site_title = "Management – C3s"
admin.site.index_title = "Welcome to Celeste's Custom Can Storage"

handler404 = "info.views.handler404"
handler401 = "info.views.handler401"
handler403 = "info.views.handler403"
handler500 = "info.views.handler500"

router = routers.DefaultRouter()
router.register("access-control-lists", AccessControlListViewSet)
router.register("cans", CanViewSet)

cans_router = CanRouter(router, "cans", lookup="can")
cans_router.register("objects", ObjectViewSet, basename="can-objects")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path(
        "api/v1/",
        include(
            [
                path("", include(router.urls)),
                path("", include(cans_router.urls)),
            ]
        ),
    ),
    re_path(
        r"^(?!(?:[._].*|accounts|admin|api|cans|c3s|favicon\.ico|media|static|.*\.txt)(?:/|$))(?P<can_name>[^/]+)/",
        include("canstorage.urls"),
    ),
    path("", include("info.urls")),
]
