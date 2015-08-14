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
"""Tests for hook scripts """

from weblate.trans.tests.test_models import RepoTestCase
from weblate.trans.scripts import run_hook


class ScriptTest(RepoTestCase):
    def test_run_hook(self):
        subproject = self.create_subproject()
        self.assertFalse(
            run_hook(subproject, 'false')
        )
        self.assertTrue(
            run_hook(subproject, 'true')
        )
