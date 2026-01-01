# -*- coding: utf-8 -*-

# Copyright (c) 2021 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import sys

if sys.version_info[0] >= 3:
    import typing as t

    if t.TYPE_CHECKING:  # pragma: no cover
        from os import stat_result  # pragma: no cover

        from ansible.module_utils.basic import AnsibleModule  # pragma: no cover


STATE_VERSION = 1


def read_file(module, path):
    # type: (AnsibleModule, str | bytes) -> bytes
    with open(path, 'rb') as f:
        return f.read()


def extract_stat(stat):
    # type: (stat_result) -> dict[str, t.Any]
    result = {
        'mode': oct(stat.st_mode)[2:],
        'inode': stat.st_ino,
        'dev': stat.st_dev,
        'nlink': stat.st_nlink,
        'uid': stat.st_uid,
        'gid': stat.st_gid,
        'size': stat.st_size,
        # 'atime': stat.st_atime,  -- we care about modifications, not about access
        'mtime': stat.st_mtime,
        'ctime': stat.st_ctime,
        'blocks': getattr(stat, 'st_blocks', None),
        'blksize': getattr(stat, 'st_blksize', None),
        'rdev': getattr(stat, 'st_rdev', None),
        'flags': getattr(stat, 'st_flags', None),
        'gen': getattr(stat, 'st_gen', None),
        'birthtime': getattr(stat, 'st_birthtime', None),
        'ftype': getattr(stat, 'st_ftype', None),
        'attrs': getattr(stat, 'st_attrs', None),
        'obtype': getattr(stat, 'st_obtype', None),
    }
    return result
