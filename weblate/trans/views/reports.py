# -*- coding: utf-8 -*-
#
# Copyright © 2012 - 2015 Michal Čihař <michal@cihar.com>
#
# This file is part of Weblate <http://weblate.org/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from weblate.trans.models.changes import Change


def generate_credits(component, start_date):
    """Generates credits data for given component."""

    result = []

    for translation in component.translation_set.all():
        authors = Change.objects.content().filter(
            translation=translation
        ).values_list(
            'author__email', 'author__first_name'
        )
        if not authors:
            continue
        result.append({translation.language.name:  sorted(set(authors))})

    return result
