# Copyright (c) 2020 Ansible
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.six import string_types as _string_types
from ansible.utils.unsafe_proxy import AnsibleUnsafe as _AnsibleUnsafe
from ansible.utils.unsafe_proxy import wrap_var as _make_unsafe

try:
    # This requires ansible-core with Data Tagging
    from ansible.utils.datatag import trust_value as _trust_value
except ImportError:
    _trust_value = None

try:
    from ansible._internal._datatag import _tags as _ansible_internal_tags
    from ansible.module_utils._internal._datatag import AnsibleTagHelper as _AnsibleTagHelper
except ImportError:
    _ansible_internal_tags = None
    _AnsibleTagHelper = None


# Whether ansible-core supports Data Tagging
SUPPORTS_DATA_TAGGING = _trust_value is not None


def make_trusted(input):
    """
    Given a value, marks it as trusted (if possible).

    This is a no-op for ansible-core versions without Data Tagging.
    There, all strings not explicitly marked as unsafe are trusted.

    Note that this does not work recursively on data structures.
    """
    if _trust_value and isinstance(input, str):
        input = _trust_value(input)
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

    This uses Data Tagging methods when ansible-core supports Data Tagging,
    and checks for AnsibleUnsafe for older ansible-core versions.

    Note that Data Tagging does not offer any method to directly test whether
    a value is trusted, so we have to use ansible-core internals.
    """
    if _ansible_internal_tags and _AnsibleTagHelper:
        # Note that this can break at any minute.
        return _ansible_internal_tags.TrustedAsTemplate in _AnsibleTagHelper.tag_types(input)

    return not isinstance(input, _AnsibleUnsafe)
