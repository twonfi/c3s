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
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from keyblade.models import Key
from keyblade import forms


@login_required
def key_management(request):
    context = {
        "title": "Key management",
        "keys": Key.objects.filter(user=request.user),
    }

    return render(request, "keyblade/keys/management.html", context)


@login_required
def create_key(request):
    if request.method == "POST":
        form = forms.CreateKeyForm(request.POST)

        if form.is_valid():
            form.user = request.user
            key = form.save(commit=False)
            key.user = request.user
            __, private_key = key.generate_key()
            key.save()

            context = {
                "title": "Key created",
                "key": key,
                "private_key": private_key,
            }

            return render(request, "keyblade/keys/created.html", context)
    else:
        form = forms.CreateKeyForm()

    context = {
        "title": "Create key",
        "form": form,
    }

    return render(request, "keyblade/keys/create.html", context)


@login_required
def revoke_key(request):
    key_ids = request.GET.getlist("keys[]")
    keys = []

    if key_ids:
        for key_id in key_ids:
            try:
                key = Key.objects.get(id=key_id, user=request.user)
            except Key.DoesNotExist:
                pass
            else:
                if not key.revoked:
                    keys.append(key)

    if not keys:
        context = {
            "title": "No keys to revoke",
        }

        return render(request, "keyblade/keys/revoke_no_keys.html", context)

    if request.method == "POST":
        for key in keys:
            key.revoked = True
            key.save()

        return redirect("keyblade:key_management")
    else:
        context = {
            "title": "Revoke keys",
            "keys": keys,
        }

        return render(request, "keyblade/keys/revoke.html", context)
