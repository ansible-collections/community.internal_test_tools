# Copyright (c) 2019-2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Small framework for testing modules which use ``fetch_url()`` from
``ansible.module_utils.urls`` to communicate with a HTTP service.

The main interface consists of the classes ``FetchUrlCall`` and
``BaseTestModule``.

A test is expected to be inherited from ``BaseTestModule``. The class
provides two methods, ``run_module_success`` and ``run_module_failed``,
which expect next to the module's Python module and the arguments a list
of ``FetchUrlCall`` objects which correspond to the expected ``fetch_url()``
calls made by the module for the given input. The methods return the
result returned by ``module.fail_json()`` and ``module.exit_json()``,
respectively.

An example test could look as follows::

    from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
        FetchUrlCall,
        BaseTestModule,
    )

    from ansible_collections.community.general.plugins.module_utils.hetzner import BASE_URL
    from ansible_collections.community.general.plugins.modules.net_tools import hetzner_firewall_info

    class TestHetznerFirewallInfo(BaseTestModule):
        MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.general.plugins.modules.net_tools.hetzner_firewall_info.AnsibleModule'
        MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.general.plugins.module_utils.hetzner.fetch_url'

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

This test makes sure that if the ``community.general.hetzner_firewall_info``
module is called with the given arguments, one ``fetch_url()`` call is made
to ``GET`` the URL, and if this call is returned with a ``200 OK`` and the
given JSON object, that the module will return ``result`` which is then
checked by the ``assert`` statements.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import json
import sys

import pytest

import ansible.module_utils.basic  # noqa: F401, pylint: disable=unused-import
import ansible.module_utils.urls  # noqa: F401, pylint: disable=unused-import

from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import MagicMock
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args

from ._utils import (
    CallBase as _CallBase,
    validate_call as _validate_call,
)

if sys.version_info[0] >= 3:
    import typing as t

    if t.TYPE_CHECKING:
        from datetime import datetime
        from http.cookiejar import CookieJar
        from types import ModuleType

        from ansible.module_utils.basic import AnsibleModule


class FetchUrlCall(_CallBase):
    '''
    Describes one call to ``fetch_url()``.

    This class contains information on what ``fetch_url()`` should return, and how to
    validate the data passed to ``fetch_url()``.
    '''

    def __init__(self, method, status):
        # type: (str, int) -> None
        '''
        Create a ``fetch_url()`` expected call. Must be passed information on the expected
        HTTP method and the HTTP status returned by the call.
        '''
        super(FetchUrlCall, self).__init__(method, status)

    def result_error(self, msg, body=None):
        # type: (str, str | bytes | None) -> t.Self
        '''
        Builder method to set return body of the call in case of an error.
        '''
        self.error_data['msg'] = msg
        if body is not None:
            self.error_data['body'] = body
            assert self.body is None, 'Result must not be given if error body is provided'
        return self

    def result_error_json(self, msg, json_body):
        # type: (str, t.Any) -> t.Self
        '''
        Builder method to set return body of the call (as a JSON object) in case of an error.
        '''
        return self.result_error(msg, body=json.dumps(json_body).encode('utf-8'))


class _ReadResponse(object):
    closed = True

    def read(self):
        # type: () -> bytes
        if sys.version_info[0] == 2:
            raise TypeError('response already read')
        return b''  # pragma: no cover


class _FetchUrlProxy(object):
    '''
    Internal proxy for ``fetch_url()``.

    Receives a list of expected ``fetch_url()`` calls, and checks the calls made
    to the proxy against the expected ones. Will raise an exception if too many
    calls are made.
    '''
    def __init__(self, calls):
        # type: (list[FetchUrlCall]) -> None
        '''
        Create instance with expected list of calls.
        '''
        self.calls = calls
        self.index = 0

    def __call__(
        self,
        module,  # type: AnsibleModule
        url,  # type: str
        data=None,  # type: str | bytes | None
        headers=None,  # type: dict[str, str] | None
        method=None,  # type: str | None
        use_proxy=True,  # type: bool
        force=False,  # type: bool
        last_mod_time=None,  # type: datetime | None
        timeout=10,  # type: int | float
        use_gssapi=False,  # type: bool
        unix_socket=None,  # type: str | None
        ca_path=None,  # type: str | None
        cookies=None,  # type: CookieJar | None
    ):
        # type: (...) -> tuple[object, dict[str, t.Any]]
        '''
        A call to ``fetch_url()``.
        '''
        assert self.index < len(self.calls), 'Got more fetch_url calls than expected'
        call = self.calls[self.index]
        self.index += 1

        # Validate call
        _validate_call(
            call, method=method, url=url, headers=headers, data=data, timeout=timeout,
            url_username=module.params.get('url_username'), url_password=module.params.get('url_password'),
            force_basic_auth=module.params.get('force_basic_auth'),
        )

        # Compose result
        info = dict(status=call.status, url=url)
        for k, v in call.headers.items():
            info[k.lower()] = v
        info.update(call.error_data)
        if call.body is not None:
            res_mock = MagicMock()
            res_mock.read = MagicMock(return_value=call.body)
            res_mock.closed = False
            res = res_mock  # type: object
        elif call.error_data:
            res = _ReadResponse()
            if 'body' not in info:
                info['body'] = b''
        else:
            res = object()
        return (res, info)

    def assert_is_done(self):
        # type: () -> None
        '''
        Assert that all expected ``fetch_url()`` calls have been made.
        '''
        assert self.index == len(self.calls), 'Got less fetch_url calls than expected (%d vs. %d)' % (self.index, len(self.calls))


class ModuleExitException(Exception):
    '''
    Sentry exception to track regular module exit.
    '''
    def __init__(self, kwargs):
        # type: (**t.Any) -> None
        self.kwargs = kwargs  # type: dict[str, t.Any]


class ModuleFailException(Exception):
    '''
    Sentry exception to track regular module failure.
    '''
    def __init__(self, kwargs):
        # type: (**t.Any) -> None
        self.kwargs = kwargs  # type: dict[str, t.Any]


class BaseTestModule(object):
    '''
    Base class for testing ``fetch_url()`` based modules.

    Provides support methods ``run_module_success()`` and ``run_module_failed()``.
    '''

    # Users of this class need to overwrite this depending on how AnsibleModule was imported in the module
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible.module_utils.basic.AnsibleModule'
    # Users of this class need to overwrite this depending on how fetch_url was imported in the module
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible.module_utils.urls.fetch_url'

    def run_module(self, mocker, module, arguments, fetch_url):
        # type: (t.Any, ModuleType, dict[str, t.Any], _FetchUrlProxy) -> None

        def exit_json(module, **kwargs):
            # type: (AnsibleModule, **t.Any) -> t.NoReturn
            module._return_formatted(kwargs)
            raise ModuleExitException(kwargs)

        def fail_json(module, **kwargs):
            # type: (AnsibleModule, **t.Any) -> t.NoReturn
            module._return_formatted(kwargs)
            raise ModuleFailException(kwargs)

        mocker.patch(self.MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL, fetch_url)
        mocker.patch(self.MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE + '.exit_json', exit_json)
        mocker.patch(self.MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE + '.fail_json', fail_json)
        with set_module_args(arguments):
            module.main()

    def run_module_success(self, mocker, module, arguments, fetch_url_calls):
        # type: (t.Any, ModuleType, dict[str, t.Any], list[FetchUrlCall] | None) -> dict[str, t.Any]
        '''
        Run module given by Python module ``module`` with the arguments ``arguments``
        and expected ``fetch_url()`` calls ``fetch_url_calls``. Expect module to exit.
        Returns expanded arguments to ``AnsibleModule.exit_json()``.
        '''
        fetch_url = _FetchUrlProxy(fetch_url_calls or [])
        with pytest.raises(ModuleExitException) as e:
            self.run_module(mocker, module, arguments, fetch_url)
        fetch_url.assert_is_done()
        return e.value.kwargs

    def run_module_failed(self, mocker, module, arguments, fetch_url_calls):
        # type: (t.Any, ModuleType, dict[str, t.Any], list[FetchUrlCall] | None) -> dict[str, t.Any]
        '''
        Run module given by Python module ``module`` with the arguments ``arguments``
        and expected ``fetch_url()`` calls ``fetch_url_calls``. Expect module to fail.
        Returns expanded arguments to ``AnsibleModule.fail_json()``.
        '''
        fetch_url = _FetchUrlProxy(fetch_url_calls or [])
        with pytest.raises(ModuleFailException) as e:
            self.run_module(mocker, module, arguments, fetch_url)
        fetch_url.assert_is_done()
        return e.value.kwargs
