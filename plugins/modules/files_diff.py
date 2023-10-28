#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: files_diff
short_description: Check whether there were changes since files_collect was called
version_added: 0.3.0
author:
  - Felix Fontein (@felixfontein)
description:
  - This module checks whether any changes (timestamps, attributes, content) were made to files
    and directories that M(community.internal_test_tools.files_collect) collected information on
    earlier.
notes:
  - Supports C(check_mode). The module never modifies anything, so check mode behavior is identical to regular behavior.

options:
  state:
    required: true
    description:
      - The state returned by M(community.internal_test_tools.files_collect).
    type: dict
  fail_on_diffs:
    description:
      - Whether to fail when differences are found, instead of simply returning RV(changed=true).
    type: bool
    default: false
'''

EXAMPLES = r'''
- name: Recursively collect information on all files in output_dir
  community.internal_test_tools.files_collect:
    directories:
      - path: "{{ output_dir }}"
  register: state

# ... some tasks in between ...

- name: Verify whether any file changed in output_dir
  community.internal_test_tools.files_diff:
    state: "{{ state.state }}"
'''

RETURN = r'''
changed:
  description:
    - Whether any file or directory changed.
    - These can be attribute changes, time changes, or content changes.
  type: bool
  returned: success
  sample: true
changed_content:
  description:
    - Whether any file content changed. This does not consider added or removed files,
      or files which were converted to links or vice versa.
  type: bool
  returned: success
  sample: true
added_files:
  description:
    - A list of files that were added.
  type: list
  elements: path
  returned: success
  sample: [file_a.txt, dir/file_b]
removed_files:
  description:
    - A list of files that were removed.
  type: list
  elements: path
  returned: success
  sample: [file_a.txt, dir/file_b]
changed_files:
  description:
    - A list of files that were changed.
    - Attribute changes, times changes, inode changes, symlink changes, and content changes are considered.
  type: list
  elements: path
  returned: success
  sample: [file_a.txt, dir/file_b]
changed_files_content:
  description:
    - A list of files whose content was changed.
    - B(Only) content changes are considered.
  type: list
  elements: path
  returned: success
  sample: [file_a.txt, dir/file_b]
added_dirs:
  description:
    - A list of directories that have been added.
  type: list
  elements: path
  returned: success
  sample: [dir_a, dir/dir_b]
removed_dirs:
  description:
    - A list of directories that have been removed.
  type: list
  elements: path
  returned: success
  sample: [dir_a, dir/dir_b]
changed_dirs:
  description:
    - A list of directories that have been changed.
  type: list
  elements: path
  returned: success
  sample: [dir_a, dir/dir_b]
'''

import os
import base64
import difflib
import hashlib

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.internal_test_tools.plugins.module_utils.state import (
    STATE_VERSION,
    read_file,
    extract_stat,
)


def compare_stat(ex_stat, path, differences_neg, differences_pos):
    stat = extract_stat(os.lstat(path))
    for k in stat:
        if stat[k] != ex_stat[k]:
            differences_neg.append('-  {key}: {value}'.format(key=k, value=ex_stat[k]))
            differences_pos.append('+  {key}: {value}'.format(key=k, value=stat[k]))


def check_file(module, path, file, global_differences, changed_files, changed_files_content, added_files, removed_files):
    differences_neg = []
    differences_pos = []
    differences = []

    ex_exist = file.get('exists', True)
    exists = os.path.exists(path)
    if ex_exist != exists:
        differences_neg.append('-  exists: {0}'.format(ex_exist))
        differences_pos.append('+  exists: {0}'.format(exists))
        if ex_exist:
            removed_files.add(path)
        else:
            added_files.add(path)

    if exists and 'stat' in file:
        compare_stat(file['stat'], path, differences_neg, differences_pos)

        ex_symlink = file.get('symlink')
        symlink = os.readlink(path) if os.path.islink(path) else None
        if ex_symlink != symlink:
            differences_neg.append('-  link: {0}'.format('(not a link)' if ex_symlink is None else ex_symlink))
            differences_pos.append('+  link: {0}'.format('(not a link)' if symlink is None else symlink))

        if symlink is None:
            if not os.path.isfile(path):
                differences_neg.append('-  type: {type}'.format(type='link' if ex_symlink is not None else 'file'))
                differences_pos.append('+  type: {type}'.format(type='directory' if os.path.isdir(path) else '???'))
            else:
                content = read_file(module, path)

                if 'sha256' in file:
                    ex_sha256 = file['sha256']
                    sha256 = hashlib.sha256(content).hexdigest()
                    if sha256 != ex_sha256:
                        changed_files_content.add(path)
                        differences_neg.append('-  SHA-256: {0}'.format(ex_sha256))
                        differences_pos.append('+  SHA-256: {0}'.format(sha256))

                if 'content' in file:
                    ex_content = base64.b64decode(file['content'])
                    if content != ex_content:
                        changed_files_content.add(path)
                        differences.append('   Content:')
                        if module._diff:
                            ex_lines = ex_content.decode('utf-8').splitlines(False)
                            lines = content.decode('utf-8').splitlines(False)
                            differences.extend([line.rstrip('\n') for line in difflib.unified_diff(ex_lines, lines, n=3)])
                        else:
                            differences.append('-     (...)')
                            differences.append('+     (...)')

    if differences or differences_pos or differences_neg:
        if ex_exist and exists:
            changed_files.add(path)
        global_differences.append('--- {path}\n+++ {path}\n{diffs}'.format(
            path=path,
            diffs='\n'.join(differences_neg + differences_pos + differences),
        ))


def is_state(state):
    return 'files' in state and 'directories' in state and state.get('version') == STATE_VERSION


def main():
    argument_spec = dict(
        state=dict(required=True, type='dict'),
        fail_on_diffs=dict(type='bool', default=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    state = module.params['state']
    if not is_state(state):
        if 'state' in state and is_state(state['state']):
            # The whole result of the previous task was passed in
            state = state['state']
        else:
            module.fail_json(msg='The value of the state parameter must be the result of community.internal_test_tools.files_collect')

    differences = []
    added_files = set()
    removed_files = set()
    changed_files = set()
    changed_files_content = set()
    added_dirs = set()
    removed_dirs = set()
    changed_dirs = set()

    for path, file in sorted(state['files'].items()):
        check_file(module, path, file, differences, changed_files, changed_files_content, added_files, removed_files)

    for path, directory in sorted(state['directories'].items()):
        if not os.path.isdir(path):
            removed_dirs.add(path)
            continue
        changed = False
        if 'stat' in directory:
            differences_neg = []
            differences_pos = []
            compare_stat(directory['stat'], path, differences_neg, differences_pos)
            if differences_neg or differences_pos:
                changed = True
                differences.append('--- {path}\n+++ {path}\n{diffs}'.format(
                    path=path,
                    diffs='\n'.join(differences_neg + differences_pos),
                ))
        for dummy, dirnames, filenames in os.walk(path):
            if 'files' in directory:
                ex_files = sorted(directory['files'])
                files = sorted(filenames)
                if ex_files != files:
                    changed = True
                    for file in files:
                        if file not in ex_files:
                            added_files.add(os.path.join(path, file))
                    modified = '{path} (files)'.format(path=path)
                    differences.append(
                        '\n'.join([
                            line.rstrip('\n') for line in difflib.unified_diff(ex_files, files, modified, modified, n=3)]))
            if 'directories' in directory:
                ex_dirs = sorted(directory['directories'])
                dirs = sorted(dirnames)
                if ex_dirs != dirs:
                    changed = True
                    for dir in ex_dirs:
                        if dir not in dirs:
                            removed_dirs.add(os.path.join(path, dir))
                    for dir in dirs:
                        if dir not in ex_dirs:
                            added_dirs.add(os.path.join(path, dir))
                    modified = '{path} (dirs)'.format(path=path)
                    differences.append(
                        '\n'.join([
                            line.rstrip('\n') for line in difflib.unified_diff(ex_dirs, dirs, modified, modified, n=3)]))
            # No recursion
            break
        if changed:
            changed_dirs.add(path)

    result = dict(
        changed=any([
            len(added_files) > 0, len(removed_files) > 0, len(changed_files) > 0,
            len(added_dirs) > 0, len(removed_dirs) > 0, len(changed_dirs) > 0,
            len(differences) > 0,
        ]),
        changed_content=len(changed_files_content) > 0,
        added_files=sorted(added_files),
        removed_files=sorted(removed_files),
        changed_files=sorted(changed_files),
        changed_files_content=sorted(changed_files_content),
        added_dirs=sorted(added_dirs),
        removed_dirs=sorted(removed_dirs),
        changed_dirs=sorted(changed_dirs),
        diff=dict(
            prepared='\n\n'.join(differences),
        ),
    )
    if result['changed'] and module.params['fail_on_diffs']:
        module.fail_json(msg='Found differences!', **result)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
