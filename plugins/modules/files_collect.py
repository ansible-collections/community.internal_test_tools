#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: files_collect
short_description: Collect state of files and directories on disk
version_added: 0.3.0
author:
  - Felix Fontein (@felixfontein)
description:
  - This module collects the state (timestamps, attributes, content) of files and directories on disk
    and returns them. Use together with M(community.internal_test_tools.files_diff) to verify later
    on whether something changed, and if yes, what exactly changed.

options:
  files:
    description:
      - List of filenames to check.
    type: list
    elements: dict
    suboptions:
      path:
        required: true
        description: Path to the directory.
        type: path
      check_content:
        description:
          - Whether to store the content of the file, or only a checksum.
          - Storing the content allows to show a diff.
        type: bool
        default: false
      allow_not_existing:
        description:
          - Whether to accept if the file does not exist (and mark it as a non-existing file in the output).
        type: bool
        default: false
  directories:
    description:
      - List of directories to check.
    type: list
    elements: dict
    suboptions:
      path:
        required: true
        description: Path to the directory.
        type: path
      check_content:
        description:
          - Whether to store the content of the files, or only a checksum.
          - Storing the content allows to show a diff.
        type: bool
        default: false
      recursive:
        description: Whether to consider subdirectories as well.
        type: bool
        default: true
'''

EXAMPLES = r'''
- name: Recursively collect information on all files in output_dir
  community.internal_test_tools.files_collect:
    directories:
      - path: "{{ output_dir }}"
  register: state

# ... some tasks inbetween ...

- name: Verify whether any file changed in output_dir
  community.internal_test_tools.files_diff:
    state: "{{ state }}"
'''

RETURN = r'''
state:
  description:
    - The state of all files and directories.
    - Use the M(community.internal_test_tools.files_diff) module to validate against the original files.
    - The structure of every field in this dictionary not explicitly documented here might change at any
      point, or might vanish alltogether without further notice. Do not rely on undocumented data!
  type: dict
  returned: success
'''

import os
import base64
import hashlib

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.internal_test_tools.plugins.module_utils.state import (
    STATE_VERSION,
    read_file,
    extract_stat,
)


def add_file(module, files, path, check_content=True, allow_not_existing=False):
    result = {}
    files[path] = result

    if not os.path.exists(path):
        if not allow_not_existing:
            module.fail_json(msg='The file "{path}" does not exist'.format(path=path))
        result['exists'] = False
        return

    stat = os.lstat(path)
    result['stat'] = extract_stat(stat)

    if os.path.islink(path):
        # Record symlink information
        result['symlink'] = os.readlink(path)
        return
    elif os.path.isfile(path):
        # Record file content
        content = read_file(module, path)
        if check_content:
            result['content'] = base64.b64encode(content)
        else:
            result['sha256'] = hashlib.sha256(content).hexdigest()
    else:
        module.fail_json('The path "{path}" is not a file or symlink - this is not yet supported!'.format(path=path))


def main():
    argument_spec = dict(
        files=dict(type='list', elements='dict', options=dict(
            path=dict(type='path', required=True),
            check_content=dict(type='bool', default=False),
            allow_not_existing=dict(type='bool', default=False),
        )),
        directories=dict(type='list', elements='dict', options=dict(
            path=dict(type='path', required=True),
            check_content=dict(type='bool', default=False),
            recursive=dict(type='bool', default=True),
        )),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    files = dict()
    directories = dict()

    for file in module.params['files'] or []:
        add_file(
            module,
            files,
            file['path'],
            check_content=file['check_content'],
            allow_not_existing=file['allow_not_existing'],
        )

    for directory in module.params['directories'] or []:
        for dirpath, dirnames, filenames in os.walk(directory['path']):
            for file in filenames:
                add_file(
                    module,
                    files,
                    os.path.join(directory['path'], dirpath, file),
                    check_content=directory['check_content'],
                    allow_not_existing=False,
                )
            directory_entry = {}
            directories[os.path.join(directory['path'], dirpath)] = directory_entry

            directory_entry['files'] = filenames
            if not directory['recursive']:
                break
            directory_entry['directories'] = dirnames

    module.exit_json(state=dict(
        changed=False,
        version=STATE_VERSION,
        files=files,
        directories=directories,
    ))


if __name__ == '__main__':
    main()
