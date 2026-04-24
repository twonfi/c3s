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
from datetime import date, timedelta

from django import forms

from keyblade import models


class CreateKeyForm(forms.ModelForm):
    class Meta:
        model = models.Key
        fields = ("expiration_date", "comment")
        widgets = {
            "expiration_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "min": (date.today() + timedelta(days=1)).isoformat(),
                }
            )
        }

    def clean_expiration_date(self):
        expiration_date = self.cleaned_data["expiration_date"]
        if expiration_date and expiration_date <= date.today():
            raise forms.ValidationError("Date must be in the future.")
        return expiration_date
