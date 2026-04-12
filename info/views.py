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

# from django.views.generic import TemplateView
from django.http import HttpResponseNotFound


# class HomeView(TemplateView):
#     template_name = "info/home.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["title"] = "Celeste's Custom Can Storage"
#         return context


def home(request):
    return HttpResponseNotFound(
        "C3s homepage is under construction\n\n(C) 2026 twonum.org / Celeste.\nAffero General Public License, version 3.",
        content_type="text/plain; charset=utf-8",
    )


# noinspection PyUnusedLocal
def handler404(request, exception):
    return HttpResponseNotFound(
        f"The path was not found on this can server.",
        content_type="text/plain; charset=utf-8",
    )
