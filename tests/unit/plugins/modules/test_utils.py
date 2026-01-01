# Copyright (c) 2025 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from .utils import extract_warnings_texts

try:
    from ansible.module_utils.common.messages import (  # type: ignore
        WarningSummary as _DT1WarningSummary,
        Detail as _DT1Detail,
    )
except ImportError:
    _DT1WarningSummary = None  # type: ignore
    _DT1Detail = None  # type: ignore


try:
    from ansible.module_utils._internal._messages import (  # type: ignore
        WarningSummary as _DT2WarningSummary,
        Event as _DT2Event,
    )
except ImportError:
    _DT2WarningSummary = None  # type: ignore
    _DT2Event = None  # type: ignore


def test_extract_warnings_texts_1():
    # type: () -> None
    assert extract_warnings_texts({}) == []
    assert extract_warnings_texts({'warnings': None}) == []
    assert extract_warnings_texts({'warnings': []}) == []
    assert extract_warnings_texts({'warnings': ['foo']}) == ['foo']


@pytest.mark.skipif(_DT1WarningSummary is None or _DT1Detail is None, reason="ansible-core does not support first iteration of Data Tagging")
def test_extract_warnings_texts_2():
    # type: () -> None
    assert extract_warnings_texts({'warnings': [_DT1WarningSummary(details=(_DT1Detail(msg='foo'), ))]}) == ['foo']  # pragma: no cover
    assert extract_warnings_texts({'warnings': [_DT1WarningSummary(details=(_DT1Detail(msg='foo'), _DT1Detail(msg='bar')))]}) == ['foo']  # pragma: no cover


@pytest.mark.skipif(_DT2WarningSummary is None or _DT2Event is None, reason="ansible-core does not support second iteration of Data Tagging")
def test_extract_warnings_texts_3():
    # type: () -> None
    warning = _DT2WarningSummary(
        event=_DT2Event(
            msg="foo",
            help_text="help text",
            formatted_traceback="traceback",
        ),
    )
    assert extract_warnings_texts({'warnings': [warning]}) == ['foo']
