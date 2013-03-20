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

from trans.machine.base import MachineTranslation, MachineTranslationError
from django.core.exceptions import ImproperlyConfigured
from weblate import appsettings

BASE_URL = 'http://api.microsofttranslator.com/V2/Ajax.svc/'
TRANSLATE_URL = BASE_URL + 'Translate'
LIST_URL = BASE_URL + 'GetLanguagesForTranslate'


def microsoft_translation_supported():
    '''
    Checks whether service is supported.
    '''
    return (
        appsettings.MT_MICROSOFT_ID is not None
        and appsettings.MT_MICROSOFT_SECRET is not None
    )


class MicrosoftTranslation(MachineTranslation):
    '''
    Microsoft Translator machine translation support.
    '''
    name = 'Microsoft'

    def __init__(self):
        '''
        Checks configuration.
        '''
        super(MicrosoftTranslation, self).__init__()
        self._access_token = None
        if not microsoft_translation_supported():
            raise ImproperlyConfigured(
                'Microsoft Translator requires credentials'
            )

    @property
    def access_token(self):
        '''
        Obtains and caches access token.
        '''
        if self._access_token is not None:
            return self._access_token

        data = self.json_req(
            'https://datamarket.accesscontrol.windows.net/v2/OAuth2-13',
            skip_auth=True,
            http_post=True,
            client_id=appsettings.MT_MICROSOFT_ID,
            client_secret=appsettings.MT_MICROSOFT_SECRET,
            scope='http://api.microsofttranslator.com',
            grant_type='client_credentials',
        )

        if 'error' in data:
            raise MachineTranslationError(
                data.get('error', 'Unknown Error') +
                data.get('error_description', 'No Error Description')
            )

        return data['access_token']

    def authenticate(self, request):
        '''
        Hook for backends to allow add authentication headers to request.
        '''
        request.add_header(
            'Authorization',
            'Bearer %s' % self.access_token
        )

    def convert_language(self, language):
        '''
        Converts language to service specific code.
        '''
        language = language.replace('_', '-').lower()
        if language == 'zh-tw':
            return 'zh-CHT'
        if language == 'zh-cn':
            return 'zh-CHS'
        return language

    def download_languages(self):
        '''
        Downloads list of supported languages from a service.
        '''
        data = self.json_req(LIST_URL)
        return data

    def format_match(self, match):
        '''
        Reformats match to (translation, quality) tuple.
        '''
        if match['quality'].isdigit():
            quality = int(match['quality'])
        else:
            quality = 0

        return (
            match['translation'],
            quality * match['match']
        )

    def download_translations(self, language, text):
        '''
        Downloads list of possible translations from a service.
        '''
        args = {
            'text': text,
            'from': 'en',
            'to': language,
            'contentType': 'text/plain',
            'category': 'general',
        }
        response = self.json_req(TRANSLATE_URL, **args)
        return [(response, 100)]
