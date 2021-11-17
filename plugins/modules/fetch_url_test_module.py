#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: fetch_url_test_module
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
    required: yes
    suboptions:
      url:
        description: The URL.
        type: str
        required: yes
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
          - Mutually exclusive with I(data_path).
        type: str
      data_path:
        description:
          - File to read data from.
          - Mutually exclusive with I(data).
        type: path
        version_added: 0.3.0
  fail_me:
    description: If set to C(true), fails the module.
    type: bool
    default: false
    version_added: 0.3.0
  set_changed:
    description: If set to C(true), claims the module changed something.
    type: bool
    default: false
    version_added: 0.3.0
'''

EXAMPLES = r'''
- name: Does nothing
  community.internal_test_tools.fetch_url_test_module:
    call_sequence: []
'''

RETURN = r'''
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
'''

import base64

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import PY3
from ansible.module_utils.urls import fetch_url


def main():
    argument_spec = dict(
        call_sequence=dict(type='list', elements='dict', required=True, options=dict(
            url=dict(type='str', required=True),
            method=dict(type='str', default='GET'),
            headers=dict(type='dict'),
            data=dict(type='str'),
            data_path=dict(type='path'),
        ), mutually_exclusive=[('data', 'data_path')]),
        fail_me=dict(type='bool', default=False),
        set_changed=dict(type='bool', default=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
    )

    results = []
    for call in module.params['call_sequence']:
        data = call['data']
        if data is not None:
            data = base64.b64decode(data)
        elif call['data_path'] is not None:
            with open(call['data_path'], 'rb') as f:
                data = f.read()
        resp, info = fetch_url(module, call['url'], method=call['method'], data=data, headers=call['headers'])
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
