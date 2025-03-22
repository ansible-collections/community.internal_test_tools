# Copyright (c) 2020 Ansible
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.six import string_types as _string_types
from ansible.utils.unsafe_proxy import AnsibleUnsafe as _AnsibleUnsafe
from ansible.utils.unsafe_proxy import wrap_var as _make_unsafe


# Whether ansible-core supports Data Tagging
SUPPORTS_DATA_TAGGING = False


def make_trusted(input):
    """
    Given a value, marks it as trusted (if possible).

    This is a no-op for ansible-core versions without Data Tagging.
    There, all strings not explicitly marked as unsafe are trusted.

    Note that this does not work recursively on data structures.
    """
    return input


def make_untrusted(input):
    """
    Given a value, marks it as untrusted.

    This works both with and without Data Tagging.

    Note that this does not work recursively on data structures.
    """
    if isinstance(input, _string_types):
        return _make_unsafe(input)
    return input


def is_trusted(input):
    """
    Given a value, checks whether it is trusted or not.

    This uses Data Tagging methods when ansible-core supports Data Tagging (not yet implemented),
    and checks for AnsibleUnsafe for older ansible-core versions.
    """
    return not isinstance(input, _AnsibleUnsafe)
