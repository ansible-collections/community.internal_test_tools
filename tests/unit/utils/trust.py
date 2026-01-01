# Copyright (c) 2020 Ansible
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys as _sys

from ansible.utils.unsafe_proxy import AnsibleUnsafe as _AnsibleUnsafe
from ansible.utils.unsafe_proxy import wrap_var as _make_unsafe

if _sys.version_info[0] == 2:
    _string_types = (basestring,)  # type: ignore # noqa: F821, pylint: disable=undefined-variable
else:
    import typing
    if typing.TYPE_CHECKING:  # pragma: no cover
        from collections.abc import Callable  # pragma: no cover

    _T = typing.TypeVar("_T")

    _string_types = (str,)

_trust_value = None  # type: Callable[[str], str] | None
_is_trusted = None  # type: Callable[[_T], bool] | None
try:
    # This requires ansible-core with Data Tagging
    from ansible.template import (  # type: ignore
        trust_as_template as _trust_value,
        is_trusted_as_template as _is_trusted,
    )
except ImportError:
    pass


# Whether ansible-core supports Data Tagging
SUPPORTS_DATA_TAGGING = _trust_value is not None


def make_trusted(input):
    # type: (_T) -> _T
    """
    Given a value, marks it as trusted (if possible).

    This is a no-op for ansible-core versions without Data Tagging.
    There, all strings not explicitly marked as unsafe are trusted.

    Note that this does not work recursively on data structures.
    """
    if _trust_value and isinstance(input, str):
        trusted_input = _trust_value(input)
        return trusted_input  # type: ignore
    return input


def make_untrusted(input):
    # type: (_T) -> _T
    """
    Given a value, marks it as untrusted.

    This works both with and without Data Tagging.

    Note that this does not work recursively on data structures.
    """
    if isinstance(input, _string_types):
        return _make_unsafe(input)  # type: ignore
    return input


def is_trusted(input):
    # type: (_T) -> bool
    """
    Given a value, checks whether it is trusted or not.

    This uses Data Tagging methods when ansible-core supports Data Tagging,
    and checks for AnsibleUnsafe for older ansible-core versions.
    """
    if _is_trusted:
        return _is_trusted(input)

    return not isinstance(input, _AnsibleUnsafe)
