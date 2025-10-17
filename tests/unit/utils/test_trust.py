# Copyright (c) 2025 Ansible
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from .trust import (
    make_trusted,
    make_untrusted,
    is_trusted,
)


def test_trust():
    # type: () -> None
    trusted = make_trusted("foo")
    untrusted = make_untrusted("bar")
    assert is_trusted(trusted)
    assert not is_trusted(untrusted)
