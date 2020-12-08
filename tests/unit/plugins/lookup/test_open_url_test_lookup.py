# (c) 2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import base64

import pytest

from ansible_collections.community.internal_test_tools.tests.unit.utils.open_url_framework import (
    OpenUrlCall,
    OpenUrlProxy,
)

from ansible_collections.community.internal_test_tools.plugins.lookup import open_url_test_lookup

from ansible.plugins.loader import lookup_loader

from ansible_collections.community.internal_test_tools.tests.unit.compat.unittest import TestCase
from ansible_collections.community.general.tests.unit.compat.mock import (
    patch,
    MagicMock,
)


class TestLookupModule(TestCase):
    def setUp(self):
        self.lookup = lookup_loader.get("community.internal_test_tools.open_url_test_lookup")

    def test_basic(self):
        open_url = OpenUrlProxy([
            OpenUrlCall('GET', 200)
            .result_str('hello')
            .expect_url('http://example.com'),
        ])
        with patch('ansible_collections.community.internal_test_tools.plugins.lookup.open_url_test_lookup.open_url', open_url):
            result = self.lookup.run(
                ['http://example.com'],
                [],
            )
        open_url.assert_is_done()

        assert len(result) == 1
        assert result[0]['status'] == 200
        assert result[0]['content'] == base64.b64encode('hello'.encode('utf-8'))
