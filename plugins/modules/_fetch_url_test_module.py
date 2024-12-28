#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: _fetch_url_test_module
short_description: Test module for fetch_url test framework (DO NOT USE THIS!)
version_added: 0.1.1
author:
  - Felix Fontein (@felixfontein)
description:
  - B(DO NOT USE THIS)!
notes:
  - Does not support C(check_mode).
options:
  call_sequence:
    description: List of HTTP calls to make.
    type: list
    elements: dict
    required: true
    suboptions:
      url:
        description: The URL.
        type: str
        required: true
      method:
        description: HTTP method.
        type: str
        default: GET
      headers:
        description: HTTP headers.
        type: dict
      data:
        description:
          - Data to send (Base64 encoded).
          - Mutually exclusive with O(call_sequence[].data_path).
        type: str
      data_path:
        description:
          - File to read data from.
          - Mutually exclusive with O(call_sequence[].data).
        type: path
        version_added: 0.3.0
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
          - Force passing C(Authorization) header on the first request when O(call_sequence[].url_username) and O(call_sequence[].url_password)
            are used.
        type: bool
        version_added: 0.7.0
  fail_me:
    description: If set to V(true), fails the module.
    type: bool
    default: false
    version_added: 0.3.0
  set_changed:
    description: If set to V(true), claims the module changed something.
    type: bool
    default: false
    version_added: 0.3.0
"""

EXAMPLES = r"""
- name: Does nothing
  community.internal_test_tools.fetch_url_test_module:
    call_sequence: []
"""

RETURN = r"""
call_results:
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

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import PY3
from ansible.module_utils.urls import fetch_url


def copy_value_if_not_none(src, key, dest):
    if key in src and src[key] is not None:
        dest[key] = src[key]
    else:
        dest.pop(key, None)


def main():
    argument_spec = dict(
        call_sequence=dict(type='list', elements='dict', required=True, options=dict(
            url=dict(type='str', required=True),
            method=dict(type='str', default='GET'),
            headers=dict(type='dict'),
            data=dict(type='str'),
            data_path=dict(type='path'),
            timeout=dict(type='float'),
            url_username=dict(type='str'),
            url_password=dict(type='str', no_log=True),
            force_basic_auth=dict(type='bool'),
        ), mutually_exclusive=[('data', 'data_path')]),
        fail_me=dict(type='bool', default=False),
        set_changed=dict(type='bool', default=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
    )

    results = []
    for call in module.params['call_sequence']:
        kwargs = {}

        data = call['data']
        if data is not None:
            kwargs['data'] = base64.b64decode(data)
        elif call['data_path'] is not None:
            with open(call['data_path'], 'rb') as f:
                kwargs['data'] = f.read()

        copy_value_if_not_none(call, 'headers', kwargs)
        copy_value_if_not_none(call, 'url_username', module.params)
        copy_value_if_not_none(call, 'url_password', module.params)
        copy_value_if_not_none(call, 'force_basic_auth', module.params)

        resp, info = fetch_url(module, call['url'], method=call['method'], **kwargs)
        try:
            # In Python 2, reading from a closed response yields a TypeError.
            # In Python 3, read() simply returns ''
            if PY3 and resp.closed:
                raise TypeError
            content = resp.read()
        except (AttributeError, TypeError):
            content = info.pop('body', None)

        if content is not None:
            content = base64.b64encode(content).decode('utf-8')
        else:
            content = ''

        results.append(dict(
            status=info['status'],
            content=content,
            headers=info,
        ))

    all_results = dict(
        call_results=results,
    )
    if module.params['set_changed']:
        all_results['changed'] = True

    if module.params['fail_me']:
        module.fail_json(msg='expected failure', **all_results)
    module.exit_json(**all_results)


if __name__ == '__main__':
    main()
