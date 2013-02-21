# -*- coding: utf-8 -*-
#
# Copyright © 2012 - 2013 Michal Čihař <michal@cihar.com>
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

from django.utils.translation import ugettext_lazy as _
from trans.checks.base import SourceCheck
import re

# Matches (s) not followed by alphanumeric chars or at the end
PLURAL_MATCH = re.compile(r'\(s\)(\W|\Z)')


class OptionalPluralCheck(SourceCheck):
    '''
    Check for not used plural form.
    '''
    check_id = 'optional_plural'
    name = _('Optional plural')
    description = _(
        'The string is optionally used as plural, but not using plural forms'
    )

    def check_source(self, source, flags, unit):
        if len(source) > 1:
            return False
        return len(PLURAL_MATCH.findall(source[0])) > 0


class EllipsisCheck(SourceCheck):
    '''
    Check for using ... instead of …
    '''
    check_id = 'ellipsis'
    name = _('Ellipsis')
    description = _(
        u'The string uses three dots (...) '
        u'instead of an ellipsis character (…)'
    )

    def check_source(self, source, flags, unit):
        return '...' in source[0]
