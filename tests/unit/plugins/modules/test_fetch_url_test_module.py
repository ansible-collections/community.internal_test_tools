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

from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args, ModuleTestCase, AnsibleExitJson


class TestFetchURLTestModule(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.internal_test_tools.plugins.modules.fetch_url_test_module.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.internal_test_tools.plugins.modules.fetch_url_test_module.fetch_url'

    def test_basic_str(self, mocker):
        result = self.run_module_success(mocker, fetch_url_test_module, {
            'call_sequence': [
                {
                    'url': 'http://example.com/',
                }
            ],
        }, [
            FetchUrlCall('GET', 200)
            .result_str('1234')
            .expect_form_value_absent('foo')
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
                }
            ],
        }, [
            FetchUrlCall('GET', 200)
            .result(b'1234')
            .expect_header_unset('foo')
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
        result = self.run_module_success(mocker, fetch_url_test_module, {
            'call_sequence': [
                {
                    'url': 'http://example.com/',
                    'data': base64.b64encode('hello'.encode('utf-8')).decode('utf-8'),
                    'headers': {
                        'foo': 'bar',
                    },
                }
            ],
        }, [
            FetchUrlCall('GET', 400)
            .result_error('meh', b'1234')
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
                    'url': 'http://example.com/',
                }
            ],
        }, [
            FetchUrlCall('GET', 400)
            .result_error('meh')
            .expect_url('http://example.com/'),
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
                    'url': 'http://example.com/',
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
            .expect_form_value_absent('bar'),
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

        assert e.value.args[0]['call_results'] == []
