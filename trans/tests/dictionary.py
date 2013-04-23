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

"""
Tests for dictionary manipulations.
"""

from trans.tests.views import ViewTestCase
from trans.models import Dictionary
from django.core.urlresolvers import reverse
from trans.tests.util import get_test_file

TEST_TBX = get_test_file('terms.tbx')
TEST_CSV = get_test_file('terms.csv')
TEST_PO = get_test_file('terms.po')


class DictionaryTest(ViewTestCase):
    '''
    Testing of dictionary manipulations.
    '''

    def get_kwargs(self):
        return {
            'lang': 'cs',
            'project': self.subproject.project.slug,
        }

    def get_url(self, url):
        return reverse(url, kwargs=self.get_kwargs())

    def import_file(self, filename, **kwargs):
        with open(filename) as handle:
            params = {'file': handle}
            params.update(kwargs)
            return self.client.post(
                self.get_url('upload_dictionary'),
                params
            )

    def test_import(self):
        '''
        Test for importing of TBX into glossary.
        '''
        show_url = self.get_url('show_dictionary')

        # Import file
        response = self.import_file(TEST_TBX)

        # Check correct response
        self.assertRedirects(response, show_url)

        # Check number of imported objects
        self.assertEquals(Dictionary.objects.count(), 164)

        # Check they are shown
        response = self.client.get(show_url)
        self.assertContains(response, u'podpůrná vrstva')

        # Change single word
        word = Dictionary.objects.get(target=u'podpůrná vrstva')
        word.target = u'zkouška sirén'
        word.save()

        # Import file again with orverwriting
        response = self.import_file(TEST_TBX, method='overwrite')

        # Check number of imported objects
        self.assertEquals(Dictionary.objects.count(), 164)

        # Check entry got overwritten
        response = self.client.get(show_url)
        self.assertContains(response, u'podpůrná vrstva')

        # Change single word
        word = Dictionary.objects.get(target=u'podpůrná vrstva')
        word.target = u'zkouška sirén'
        word.save()

        # Import file again with adding
        response = self.import_file(TEST_TBX, method='add')

        # Check number of imported objects
        self.assertEquals(Dictionary.objects.count(), 165)

    def test_import_csv(self):
        # Import file
        response = self.import_file(TEST_CSV)

        # Check correct response
        self.assertRedirects(response, self.get_url('show_dictionary'))

        # Check number of imported objects
        self.assertEquals(Dictionary.objects.count(), 164)

    def test_import_po(self):
        # Import file
        response = self.import_file(TEST_PO)

        # Check correct response
        self.assertRedirects(response, self.get_url('show_dictionary'))

        # Check number of imported objects
        self.assertEquals(Dictionary.objects.count(), 164)

    def test_edit(self):
        '''
        Test for manually adding words to glossary.
        '''
        show_url = self.get_url('show_dictionary')
        edit_url = self.get_url('edit_dictionary')
        delete_url = self.get_url('delete_dictionary')

        # Add word
        response = self.client.post(
            show_url,
            {'source': 'source', 'target': u'překlad'}
        )

        # Check correct response
        self.assertRedirects(response, show_url)

        # Check number of objects
        self.assertEquals(Dictionary.objects.count(), 1)

        dict_id = Dictionary.objects.all()[0].id
        dict_id_url = '?id=%d' % dict_id

        # Check they are shown
        response = self.client.get(show_url)
        self.assertContains(response, u'překlad')

        # Edit page
        response = self.client.get(edit_url + dict_id_url)
        self.assertContains(response, u'překlad')

        # Edit translation
        response = self.client.post(
            edit_url + dict_id_url,
            {'source': 'src', 'target': u'přkld'}
        )
        self.assertRedirects(response, show_url)

        # Check they are shown
        response = self.client.get(show_url)
        self.assertContains(response, u'přkld')

        # Test deleting
        response = self.client.post(delete_url, {'id': dict_id})
        self.assertRedirects(response, show_url)

        # Check number of objects
        self.assertEquals(Dictionary.objects.count(), 0)

    def test_download(self):
        '''
        Test for downloading files.
        '''
        # Import test data
        self.import_file(TEST_TBX)

        download_url = self.get_url('download_dictionary')

        # CSV download
        response = self.client.get(download_url + '?format=csv')
        self.assertContains(
            response,
            u'addon,doplněk'
        )

        # TBX download
        response = self.client.get(download_url + '?format=tbx')
        self.assertContains(
            response,
            u'<term>website</term>'
        )
        self.assertContains(
            response,
            u'<term>webové stránky</term>'
        )

        # PO download
        response = self.client.get(download_url + '?format=po')
        self.assertContains(
            response,
            u'msgid "wizard"\nmsgstr "průvodce"'
        )

    def test_list(self):
        '''
        Test for listing dictionaries.
        '''
        self.import_file(TEST_TBX)

        # List dictionaries
        response = self.client.get(reverse(
            'show_dictionaries',
            kwargs=self.kw_project
        ))
        self.assertContains(response, 'Czech')
        self.assertContains(response, 'Italian')

        dict_url = self.get_url('show_dictionary')

        # List all words
        response = self.client.get(dict_url)
        self.assertContains(response, 'Czech')
        self.assertContains(response, '1 / 7')
        self.assertContains(response, u'datový tok')

        # Filtering by letter
        response = self.client.get(dict_url, {'letter': 'b'})
        self.assertContains(response, 'Czech')
        self.assertContains(response, '1 / 1')
        self.assertContains(response, u'datový tok')
