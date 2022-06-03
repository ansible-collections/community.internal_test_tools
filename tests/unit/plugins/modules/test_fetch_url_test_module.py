# (c) 2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import base64

import pytest

from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.internal_test_tools.plugins.modules import fetch_url_test_module

from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import mock_open

from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    set_module_args,
    ModuleTestCase,
    AnsibleExitJson,
    AnsibleFailJson,
)


class TestFetchURLTestModule(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.internal_test_tools.plugins.modules.fetch_url_test_module.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.internal_test_tools.plugins.modules.fetch_url_test_module.fetch_url'

    def test_basic_str(self, mocker):
        result = self.run_module_success(mocker, fetch_url_test_module, {
            'call_sequence': [
                {
                    'url': 'http://example.com/',
                    'timeout': 10,
                }
            ],
        }, [
            FetchUrlCall('GET', 200)
            .result_str('1234')
            .expect_form_value_absent('foo')
            .expect_timeout(10)
            .expect_url('http://example.com/'),
        ])
        assert len(result['call_results']) == 1
        assert result['call_results'][0]['status'] == 200
        assert result['call_results'][0]['content'] == base64.b64encode(b'1234').decode('utf-8')

    def test_basic_auth(self, mocker):
        result = self.run_module_success(mocker, fetch_url_test_module, {
            'call_sequence': [
                {
                    'url': 'http://example.com/',
                    'url_username': 'foo',
                    'url_password': 'bar',
                    'force_basic_auth': True,
                }
            ],
        }, [
            FetchUrlCall('GET', 200)
            .result_str('1234')
            .expect_form_value_absent('foo')
            .expect_basic_auth('foo', 'bar')
            .expect_force_basic_auth(True)
            .expect_url('http://example.com/'),
        ])
        assert len(result['call_results']) == 1
        assert result['call_results'][0]['status'] == 200
        assert result['call_results'][0]['content'] == base64.b64encode(b'1234').decode('utf-8')

    def test_basic_bytes(self, mocker):
        result = self.run_module_success(mocker, fetch_url_test_module, {
            'call_sequence': [
                {
                    'url': 'http://example.com/',
                    'force_basic_auth': False,
                }
            ],
        }, [
            FetchUrlCall('GET', 200)
            .result(b'1234')
            .expect_header_unset('foo')
            .expect_force_basic_auth(False)
            .expect_url('http://example.com/'),
        ])
        assert len(result['call_results']) == 1
        assert result['call_results'][0]['status'] == 200
        assert result['call_results'][0]['content'] == base64.b64encode(b'1234').decode('utf-8')

    def test_basic_json(self, mocker):
        result = self.run_module_success(mocker, fetch_url_test_module, {
            'call_sequence': [
                {
                    'url': 'http://example.com/',
                }
            ],
        }, [
            FetchUrlCall('GET', 200)
            .result_json(dict(foo='bar'))
            .return_header('Foo', 'bar')
            .expect_url('http://example.com/'),
        ])
        assert len(result['call_results']) == 1
        assert result['call_results'][0]['status'] == 200
        assert result['call_results'][0]['headers']['foo'] == 'bar'

    def test_with_data(self, mocker):
        mocker.patch('ansible_collections.community.internal_test_tools.plugins.modules.fetch_url_test_module.open', mock_open(read_data=b'\x00\x01\x02'))
        result = self.run_module_success(mocker, fetch_url_test_module, {
            'call_sequence': [
                {
                    'url': 'http://example.com/',
                    'data_path': '/data',
                    'headers': {
                        'foo': 'bar',
                    },
                }
            ],
        }, [
            FetchUrlCall('GET', 400)
            .result_error('meh', b'1234')
            .expect_content(b'\x00\x01\x02')
            .expect_content_predicate(lambda content: True)
            .expect_header('foo', 'bar')
            .expect_header_unset('baz')
            .expect_url('http://example.com/'),
        ])
        assert len(result['call_results']) == 1
        assert result['call_results'][0]['status'] == 400
        assert result['call_results'][0]['content'] == base64.b64encode(b'1234').decode('utf-8')

    def test_with_no_result(self, mocker):
        result = self.run_module_success(mocker, fetch_url_test_module, {
            'call_sequence': [
                {
                    'url': 'http://example.com/?foo',
                }
            ],
        }, [
            FetchUrlCall('GET', 400)
            .result_error('meh')
            .expect_url('http://example.com/', without_query=True, without_fragment=True)
            .expect_query_values('foo', ''),
        ])
        assert len(result['call_results']) == 1
        assert result['call_results'][0]['status'] == 400
        assert result['call_results'][0]['content'] == ''

    def test_failure(self, mocker):
        result = self.run_module_failed(mocker, fetch_url_test_module, {
            'call_sequence': [
                {
                    'url': 'http://example.com/',
                }
            ],
            'fail_me': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_str('1234')
            .expect_url('http://example.com/'),
        ])
        assert result['msg'] == 'expected failure'
        assert len(result['call_results']) == 1
        assert result['call_results'][0]['status'] == 200
        assert result['call_results'][0]['content'] == base64.b64encode(b'1234').decode('utf-8')

    def test_form(self, mocker):
        result = self.run_module_success(mocker, fetch_url_test_module, {
            'call_sequence': [
                {
                    'url': 'http://example.com?bar=foo&foo=bar&foo=baz#heyhey',
                    'data': base64.b64encode('foo=bar&baz=baz%20baz'.encode('utf-8')).decode('utf-8'),
                    'headers': {
                        'Content-type': 'application/x-www-form-urlencoded',
                    },
                }
            ],
        }, [
            FetchUrlCall('GET', 200)
            .expect_form_present('foo')
            .expect_form_value('baz', 'baz baz')
            .expect_form_value_absent('bar')
            .expect_url('http://example.com', without_query=True, without_fragment=True)
            .expect_query_values('bar', 'foo')
            .expect_query_values('foo', 'bar', 'baz'),
        ])
        assert len(result['call_results']) == 1
        assert result['call_results'][0]['status'] == 200

    def test_json(self, mocker):
        result = self.run_module_success(mocker, fetch_url_test_module, {
            'call_sequence': [
                {
                    'url': 'http://example.com?#heyhey',
                    'data': base64.b64encode('{"a": "b", "c": ["d"]}'.encode('utf-8')).decode('utf-8'),
                    'headers': {
                        'Content-type': 'application/x-www-form-urlencoded',
                    },
                }
            ],
        }, [
            FetchUrlCall('GET', 200)
            .expect_json_present(['a'])
            .expect_json_value(['c', 0], 'd')
            .expect_json_value_absent(['b'])
            .expect_url('http://example.com', without_query=True, without_fragment=True),
        ])
        assert len(result['call_results']) == 1
        assert result['call_results'][0]['status'] == 200


class TestFetchURLTestModule2(ModuleTestCase):
    # Test for ModuleTestCase

    def test_basic(self):
        with pytest.raises(AnsibleExitJson) as e:
            set_module_args({
                'call_sequence': [],
                '_ansible_remote_tmp': '/tmp/tmp',
                '_ansible_keep_remote_files': True,
            })
            fetch_url_test_module.main()

        assert not e.value.args[0]['changed']
        assert e.value.args[0]['call_results'] == []

    def test_basic_changed(self):
        with pytest.raises(AnsibleExitJson) as e:
            set_module_args({
                'call_sequence': [],
                'set_changed': True,
            })
            fetch_url_test_module.main()

        assert e.value.args[0]['changed']
        assert e.value.args[0]['call_results'] == []

    def test_fail(self):
        with pytest.raises(AnsibleFailJson) as e:
            set_module_args({
                'call_sequence': [],
                'fail_me': True,
            })
            fetch_url_test_module.main()

        assert e.value.args[0]['call_results'] == []
