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


class TestFetchURLTestModule(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.internal_test_tools.plugins.modules.fetch_url_test_module.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.internal_test_tools.plugins.modules.fetch_url_test_module.fetch_url'

    def test_basic(self, mocker):
        result = self.run_module_success(mocker, fetch_url_test_module, {
            'call_sequence': [
                {
                    'url': 'http://example.com/',
                }
            ],
        }, [
            FetchUrlCall('GET', 200)
            .result(b'1234')
            .expect_url('http://example.com/'),
        ])
        assert len(result['call_results']) == 1
        assert result['call_results'][0]['status'] == 200
        assert result['call_results'][0]['content'] == base64.b64encode(b'1234').decode('utf-8')
