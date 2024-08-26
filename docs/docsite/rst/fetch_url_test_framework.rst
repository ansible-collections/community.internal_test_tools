..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.internal_test_tools.docsite.fetch_url_test_framework:

``fetch_url`` Test Framework
============================

The ``fetch_url`` test framework is a small framework for testing modules which use ``fetch_url()`` from ``ansible.module_utils.urls`` to communicate with a HTTP service. It is available from ``ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework``.

The main interface consists of the classes ``FetchUrlCall`` and ``BaseTestModule``. A test is expected to be inherited from ``BaseTestModule``. The class provides two methods, ``run_module_success`` and ``run_module_failed``, which expect next to the module's Python module and the arguments a list of ``FetchUrlCall`` objects which correspond to the expected ``fetch_url()`` calls made by the module for the given input. The methods return the result returned by ``module.fail_json()`` and ``module.exit_json()``, respectively.

Several unit tests using this framework can be found in `the community.hrobot module unit tests <https://github.com/ansible-collections/community.hrobot/tree/main/tests/unit/plugins/modules>`_.

Example unit test
-----------------

An example test could look as follows:

.. code-block:: python

    from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
        FetchUrlCall,
        BaseTestModule,
    )

    from ansible_collections.community.general.plugins.module_utils.hetzner import BASE_URL
    from ansible_collections.community.general.plugins.modules.net_tools import hetzner_firewall_info

    class TestHetznerFirewallInfo(BaseTestModule):
        # We need to tell the helper under which names the module imports AnsibleModule and fetch_url
        MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = (
            'ansible_collections.community.general.plugins.modules.net_tools.hetzner_firewall_info.AnsibleModule'
        )
        MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = (
            'ansible_collections.community.general.plugins.module_utils.hetzner.fetch_url'
        )

        def test_absent(self, mocker):
            result = self.run_module_success(mocker, hetzner_firewall_info, {
                'hetzner_user': '',
                'hetzner_password': '',
                'server_ip': '1.2.3.4',
            }, [
                FetchUrlCall('GET', 200)
                .result_json({
                    'firewall': {
                        'server_ip': '1.2.3.4',
                        'server_number': 1,
                        'status': 'disabled',
                        'port': 'main',
                        'rules': {
                            'input': [],
                        },
                    },
                })
                .expect_url('{0}/firewall/1.2.3.4'.format(BASE_URL)),
            ])
            assert result['changed'] is False
            assert result['firewall']['status'] == 'disabled'
            assert result['firewall']['server_ip'] == '1.2.3.4'
            assert result['firewall']['server_number'] == 1

This test makes sure that if the :ansplugin:`community.general.hetzner_firewall_info#module` module is called with the given arguments, one ``fetch_url()`` call is made to ``GET`` the URL, and if this call is returned with a ``200 OK`` and the given JSON object, that the module will return ``result`` which is then checked by the ``assert`` statements.
