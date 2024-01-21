# Copyright (c) 2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

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

# This import is needed so patching below works
from ansible_collections.community.internal_test_tools.plugins.lookup import _open_url_test_lookup  # noqa: F401, pylint: disable=unused-import

from ansible_collections.community.internal_test_tools.tests.unit.compat.unittest import TestCase
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch


class TestLookupModule(TestCase):
    def setUp(self):
        self.lookup = lookup_loader.get("community.internal_test_tools._open_url_test_lookup")

    def test_basic(self):
        open_url = OpenUrlProxy([
            OpenUrlCall('GET', 200)
            .result_str('hello')
            .expect_form_value_absent('foo')
            .expect_header_unset('foo')
            .expect_url('http://example.com'),
        ])
        with patch('ansible_collections.community.internal_test_tools.plugins.lookup._open_url_test_lookup.open_url', open_url):
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
            .expect_content('name=foo&email=name@example.com'.encode('utf-8'))
            .expect_content_predicate(lambda content: True)
            .expect_header('foo', 'bar')
            .expect_header_unset('baz'),
            OpenUrlCall('POST', 500)
            .result_error('Error!'.encode('utf-8'))
            .expect_form_present('name')
            .expect_form_value('email', 'name@example.com')
            .expect_form_value_absent('firstname')
            .expect_url('http://example.org'),
            OpenUrlCall('POST', 400)
            .result_error()
            .expect_url('http://example.example'),
        ])
        with patch('ansible_collections.community.internal_test_tools.plugins.lookup._open_url_test_lookup.open_url', open_url):
            result = self.lookup.run(
                ['http://example.com', 'http://example.org', 'http://example.example'],
                [],
                method='POST',
                headers=dict(foo='bar'),
                data=base64.b64encode('name=foo&email=name@example.com'.encode('utf-8')).decode('utf-8'),
            )
        open_url.assert_is_done()

        assert len(result) == 3
        assert result[0]['status'] == 200
        assert result[1]['status'] == 500
        assert result[2]['status'] == 400
        assert result[2]['content'] == ''

    def test_error(self):
        open_url = OpenUrlProxy([
            OpenUrlCall('PUT', 404)
            .exception(lambda: Exception('foo bar!'))
            .expect_header('foo', 'bar')
            .expect_header_unset('baz')
            .expect_url('http://example.com', without_query=True, without_fragment=True)
            .expect_query_values('foo', ''),
        ])
        with patch('ansible_collections.community.internal_test_tools.plugins.lookup._open_url_test_lookup.open_url', open_url):
            with pytest.raises(AnsibleLookupError) as e:
                self.lookup.run(
                    ['http://example.com?foo', 'http://example.org'],
                    [],
                    method='PUT',
                    headers=dict(foo='bar'),
                )
        open_url.assert_is_done()

        print(e.value.message)
        assert e.value.message == 'Error while PUTing http://example.com?foo: foo bar!'

    def test_error_in_test(self):
        open_url = OpenUrlProxy([
            OpenUrlCall('GET', 204)
            .expect_url('http://example.com#asdf', without_query=True)
            .expect_query_values('foo', 'bar', 'baz'),
        ])
        with patch('ansible_collections.community.internal_test_tools.plugins.lookup._open_url_test_lookup.open_url', open_url):
            with pytest.raises(AnsibleLookupError) as e:
                self.lookup.run(
                    ['http://example.com?foo=bar&foo=baz#asdf', 'http://example.org'],
                    [],
                )
        open_url.assert_is_done()

        print(e.value.message)
        assert e.value.message == 'Error while GETing http://example.com?foo=bar&foo=baz#asdf: OpenUrlCall data has neither body nor error data'
