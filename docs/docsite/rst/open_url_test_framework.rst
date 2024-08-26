..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.internal_test_tools.docsite.open_url_test_framework:

``open_url`` Test Framework
===========================

The ``open_url`` test framework is a small unit test framework for testing modules and plugins which use ``open_url()`` from ``ansible.module_utils.urls`` to communicate with a HTTP service. It is available from ``ansible_collections.community.internal_test_tools.tests.unit.utils.open_url_framework``.

The main interface consists of the classes ``OpenUrlCall`` and ``OpenUrlProxy``. Tests are expected to mock ``open_url`` with an instance of ``OpenUrlProxy``, and to call its ``assert_is_done`` at the end of the test.

Several unit tests using this framework can be found in `the community.dns inventory plugin unit tests <https://github.com/ansible-collections/community.dns/tree/main/tests/unit/plugins/inventory>`_.

Example unit test
-----------------

An example unit test could look as follows:

.. code-block:: python

    import base64

    from ansible.plugins.loader import lookup_loader

    from ansible_collections.community.internal_test_tools.tests.unit.utils.open_url_framework import (
        OpenUrlCall,
        OpenUrlProxy,
    )

    # This import is needed so patching below works
    from ansible_collections.community.internal_test_tools.plugins.lookup import _open_url_test_lookup  # noqa

    from ansible_collections.community.internal_test_tools.tests.unit.compat.unittest import TestCase
    from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch


    class TestLookupModule(TestCase):
        def setUp(self):
            self.lookup = lookup_loader.get("community.internal_test_tools._open_url_test_lookup")

        def test_basic(self):
            open_url = OpenUrlProxy([
                OpenUrlCall('GET', 200)
                .result_str('hello')
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

This test makes sure that if the :ansplugin:`community.internal_test_tools._open_url_test_lookup#lookup` lookup makes the requested ``open_url()`` call.
