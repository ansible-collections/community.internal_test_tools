#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: fetch_url_test_module
short_description: Test module for fetch_url test framework
author:
  - Felix Fontein (@felixfontein)
description:
  - Don't use this.

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
        description: Data to send (Base64 encoded).
        type: str
'''

EXAMPLES = r'''
- community.internal_test_tools:
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
'''

import base64

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


def main():
    argument_spec = dict(
        call_sequence=dict(type='list', elements='dict', required=True, options=dict(
            url=dict(type='str', required=True),
            method=dict(type='str', default='GET'),
            headers=dict(type='dict'),
            data=dict(type='str'),
        ))
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
    )

    results = []
    for call in module.params['call_sequence']:
        data = call['data']
        if data is not None:
            data = base64.b64decode(data)
        resp, info = fetch_url(module, call['url'], method=call['method'], data=data, headers=call['headers'])
        try:
            content = resp.read()
        except AttributeError:
            content = info.pop('body', None)

        if content is not None:
            content = base64.b64encode(content)
        else:
            content = ''

        results.append(dict(
            status=info['status'],
            content=content,
            headers=info,
        ))

    module.exit_json(call_results=results)


if __name__ == '__main__':
    main()
