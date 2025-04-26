# -*- coding: utf-8 -*-

# Copyright (c) 2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r"""
name: _open_url_test_lookup
short_description: Test plugin for the open_url test framework (DO NOT USE THIS!)
version_added: 0.3.0
author:
  - Felix Fontein (@felixfontein)
description:
  - B(DO NOT USE THIS)!
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
  timeout:
    description:
      - Timeout in seconds.
    type: float
    version_added: 0.7.0
  url_username:
    description:
      - The username for use with HTTP Basic Authentication.
    type: str
    version_added: 0.7.0
  url_password:
    description:
      - The password for use with HTTP Basic Authentication.
    type: str
    version_added: 0.7.0
  force_basic_auth:
    description:
      - Force passing C(Authorization) header on the first request when O(url_username) and O(url_password) are used.
    type: bool
    version_added: 0.7.0
"""

EXAMPLES = r"""
---
- name: Do a lookup
  ansible.builtin.debug:
    msg: "{{ lookup('community.internal_test_tools.open_url_test_lookup', 'https://example.com', method='GET', headers={'foo':
      'bar'}) }}"
"""

RETURN = r"""
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
  sample:
    - status: 200
      content: 1.2.3.4
      headers: {}
"""

import base64

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.error import HTTPError

from ansible.utils.display import Display

display = Display()


class LookupModule(LookupBase):
    def set_non_none_option(self, dest, key):
        value = self.get_option(key)
        if value is not None:
            dest[key] = value

    def run(self, terms, variables=None, **kwargs):
        self.set_options(direct=kwargs)

        method = self.get_option('method')
        data = self.get_option('data')
        if data is not None:
            data = base64.b64decode(data)

        result = []

        for url in terms:
            kwargs = {}
            self.set_non_none_option(kwargs, 'headers')
            self.set_non_none_option(kwargs, 'timeout')
            self.set_non_none_option(kwargs, 'url_username')
            self.set_non_none_option(kwargs, 'url_password')
            self.set_non_none_option(kwargs, 'force_basic_auth')
            if data is not None:
                kwargs['data'] = data
            try:
                response = open_url(url, method=method, **kwargs)
                content = response.read()
                headers = dict(sorted(response.headers.items()))
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
