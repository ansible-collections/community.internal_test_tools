# (c) 2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import base64

import pytest

from ansible.errors import AnsibleLookupError
from ansible.plugins.loader import lookup_loader

from ansible_collections.community.internal_test_tools.tests.unit.utils.open_url_framework import (
    OpenUrlCall,
    OpenUrlProxy,
)

from ansible_collections.community.internal_test_tools.plugins.lookup import open_url_test_lookup

from ansible_collections.community.internal_test_tools.tests.unit.compat.unittest import TestCase
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import (
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
        assert result[0]['content'] == base64.b64encode('hello'.encode('utf-8')).decode('utf-8')

    def test_multiple(self):
        open_url = OpenUrlProxy([
            OpenUrlCall('POST', 200)
            .result_json({'1': 2})
            .return_header('content-type', 'application/json')
            .expect_header('foo', 'bar')
            .expect_header_unset('baz')
            .expect_url('http://example.com'),
            OpenUrlCall('POST', 500)
            .result_error('Error!'.encode('utf-8'))
            .expect_form_present('name')
            .expect_form_value('email', 'name@example.com')
            .expect_form_value_absent('firstname')
            .expect_url('http://example.org'),
        ])
        with patch('ansible_collections.community.internal_test_tools.plugins.lookup.open_url_test_lookup.open_url', open_url):
            result = self.lookup.run(
                ['http://example.com', 'http://example.org'],
                [],
                method='POST',
                headers=dict(foo='bar'),
                data=base64.b64encode('name=foo&email=name@example.com'.encode('utf-8')).decode('utf-8'),
            )
        open_url.assert_is_done()

        assert len(result) == 2
        assert result[0]['status'] == 200
        assert result[1]['status'] == 500

    def test_error(self):
        open_url = OpenUrlProxy([
            OpenUrlCall('PUT', 404)
            .exception(lambda: Exception('foo bar!'))
            .expect_header('foo', 'bar')
            .expect_header_unset('baz')
            .expect_url('http://example.com'),
        ])
        with patch('ansible_collections.community.internal_test_tools.plugins.lookup.open_url_test_lookup.open_url', open_url):
            with pytest.raises(AnsibleLookupError) as e:
                self.lookup.run(
                    ['http://example.com', 'http://example.org'],
                    [],
                    method='PUT',
                    headers=dict(foo='bar'),
                )
        open_url.assert_is_done()

        assert e.value.message == 'Error while PUTing http://example.com: foo bar!'
