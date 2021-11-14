# (c) 2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from distutils.version import LooseVersion

import pytest

from ansible.release import __version__ as ansible_core_version

from ansible_collections.community.internal_test_tools.tools.run import (
    get_default_container_2_12,
    get_default_container_pre_2_12,
)


@pytest.mark.skipif(LooseVersion(ansible_core_version) < LooseVersion('2.12'), reason='Only applies for ansible-core 2.12+')
def test_get_default_container_2_12():
    assert get_default_container_2_12() is not None


@pytest.mark.skipif(LooseVersion(ansible_core_version) >= LooseVersion('2.12'), reason='Only applies for ansible-core < 2.12')
def test_get_default_container_pre_2_12():
    assert get_default_container_pre_2_12() is not None
