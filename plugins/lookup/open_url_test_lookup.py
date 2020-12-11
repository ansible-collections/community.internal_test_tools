# -*- coding: utf-8 -*-

# (c) 2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = """
---
lookup: open_url_test_lookup
short_description: Test plugin for the open_url test framework
version_added: 0.3.0
author:
  - Felix Fontein (@felixfontein)
description:
  - Don't use this.

options:
    _terms:
        description: URLs to query.
        required: true
        type: list
        elements: str
    method:
        description: HTTP method.
        type: str
        default: GET
    headers:
        description: HTTP headers.
        type: dict
    data:
        description: Data to send (Base64 encoded).
        type: str
"""

EXAMPLES = """
- ansible.builtin.debug:
    msg: "{{ lookup('community.internal_test_tools.open_url_test_lookup', 'https://example.com', method='GET', headers={'foo': 'bar'}) }}"
"""

RETURN = """
_raw:
    description: Results of HTTP calls.
    type: list
    elements: dict
    returned: success
    contains:
        status:
            description: HTTP status of request.
            type: int
            sample: 200
        content:
            description: Content (Base64 encoded).
            type: str
            sample: 1.2.3.4
        headers:
            description: Headers.
            type: dict
            sample: {}
"""

import base64

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.error import HTTPError

from ansible.utils.display import Display

display = Display()


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        self.set_options(direct=kwargs)

        method = self.get_option('method')
        headers = self.get_option('headers')
        data = self.get_option('data')
        if data is not None:
            data = base64.b64decode(data)

        result = []

        for url in terms:
            try:
                response = open_url(url, method=method, headers=headers, data=data)
                content = response.read()
                headers = dict([(k, v) for k, v in response.headers.items()])
                code = response.code
            except HTTPError as exc:
                try:
                    content = exc.read()
                except AttributeError:
                    content = b''
                headers = dict(exc.info())
                code = exc.code
            except Exception as exc:
                raise AnsibleLookupError('Error while {method}ing {url}: {error}'.format(
                    method=method,
                    url=url,
                    error=str(exc),
                ))

            result.append(dict(
                status=code,
                content=base64.b64encode(content).decode('utf-8') if content is not None else '',
                headers=headers,
            ))

        return result
