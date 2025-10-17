# Copyright (c) 2025 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from .utils import extract_warnings_texts

try:
    from ansible.module_utils.common.messages import (  # type: ignore
        WarningSummary as _WarningSummary,
        Detail as _Detail,
    )
except ImportError:
    _WarningSummary = None
    _Detail = None


def test_extract_warnings_texts_1():
    # type: () -> None
    assert extract_warnings_texts({}) == []
    assert extract_warnings_texts({'warnings': None}) == []
    assert extract_warnings_texts({'warnings': []}) == []
    assert extract_warnings_texts({'warnings': ['foo']}) == ['foo']


@pytest.mark.skipif(_WarningSummary is None or _Detail is None, reason="ansible-core does not support Data Tagging")
def test_extract_warnings_texts_2():
    # type: () -> None
    assert extract_warnings_texts({'warnings': [_WarningSummary(details=(_Detail(msg='foo'), ))]}) == ['foo']
    assert extract_warnings_texts({'warnings': [_WarningSummary(details=(_Detail(msg='foo'), _Detail(msg='bar')))]}) == ['foo']
