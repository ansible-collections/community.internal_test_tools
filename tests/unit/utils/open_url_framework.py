# Copyright (c) 2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Small framework for testing modules and plugins which use ``open_url()`` from
``ansible.module_utils.urls`` to communicate with a HTTP service.

The main interface consists of the classes ``OpenUrlCall`` and
``OpenUrlProxy``.

Tests are expected to mock ``open_url`` with an instance of ``OpenUrlProxy``,
and to call its ``assert_is_done`` at the end of the test.

An example test could look as follows::

    import base64

    from ansible.plugins.loader import lookup_loader

    from ansible_collections.community.internal_test_tools.tests.unit.utils.open_url_framework import (
        OpenUrlCall,
        OpenUrlProxy,
    )

    # This import is needed so patching below works
    from ansible_collections.community.internal_test_tools.plugins.lookup import open_url_test_lookup  # noqa

    from ansible_collections.community.internal_test_tools.tests.unit.compat.unittest import TestCase
    from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch


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

This test makes sure that if the ``community.internal_test_tools.open_url_test_lookup`` lookup
makes the requested ``open_url()`` call.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import json

from ._utils import (
    CallBase as _CallBase,
    validate_call as _validate_call,
)
from ..compat.mock import MagicMock

try:
    from urllib.error import HTTPError
except ImportError:
    # Python 2.x fallback:
    from urllib2 import HTTPError  # type: ignore


class OpenUrlCall(_CallBase):
    '''
    Describes one call to ``open_url()``.

    This class contains information on what ``open_url()`` should return, and how to
    validate the data passed to ``open_url()``.
    '''

    def __init__(self, method, status):
        '''
        Create a ``open_url()`` expected call. Must be passed information on the expected
        HTTP method and the HTTP status returned by the call.
        '''
        super(OpenUrlCall, self).__init__(method, status)
        self.exception_generator = None

    def exception(self, exception_generator):
        '''
        Builder method to raise an exception in the ``open_url()`` call.
        Must be a function that returns an exception.
        '''
        self.exception_generator = exception_generator
        assert self.error_data.get('body') is None, 'Error body must not be given'
        assert self.body is None, 'Result must not be given if exception generator is provided'
        return self

    def result(self, body):
        '''
        Builder method to set return body of the ``open_url()`` call. Must be a bytes string.
        '''
        assert self.exception_generator is None, 'Exception generator must not be given if body is provided'
        return super(OpenUrlCall, self).result(body)

    def result_error(self, body=None):
        '''
        Builder method to set return body of the ``open_url()`` call in case of an error.
        '''
        self.error_data['body'] = body
        if body is not None:
            assert self.body is None, 'Result must not be given if error body is provided'
        assert self.exception_generator is None, 'Exception generator must not be given if error is provided'
        return self

    def result_error_json(self, json_body):
        '''
        Builder method to set return body of the ``open_url()`` call (as a JSON object) in case of an error.
        '''
        return self.result_error(body=json.dumps(json_body).encode('utf-8'))


class OpenUrlProxy(object):
    '''
    Proxy for ``open_url()``.

    Receives a list of expected ``open_url()`` calls, and checks the calls made
    to the proxy against the expected ones. Will raise an exception if too many
    calls are made.
    '''
    def __init__(self, calls):
        '''
        Create instance with expected list of calls.
        '''
        self.calls = calls
        self.index = 0

    def __call__(self, url, data=None, headers=None, method=None, use_proxy=True,
                 force=False, last_mod_time=None, timeout=10, validate_certs=True,
                 url_username=None, url_password=None, http_agent=None,
                 force_basic_auth=False, follow_redirects='urllib2',
                 client_cert=None, client_key=None, cookies=None,
                 use_gssapi=False, unix_socket=None, ca_path=None,
                 unredirected_headers=None):
        '''
        A call to ``open_url()``.
        '''
        assert self.index < len(self.calls), 'Got more open_url calls than expected'
        call = self.calls[self.index]
        self.index += 1

        # Validate call
        _validate_call(
            call, method=method, url=url, headers=headers, data=data, timeout=timeout,
            url_username=url_username, url_password=url_password,
            force_basic_auth=force_basic_auth,
        )

        # Compose result
        if call.exception_generator:
            raise call.exception_generator()
        info = dict()
        for k, v in call.headers.items():
            info[k.lower()] = v
        if call.body is not None:
            res = MagicMock()
            res.read = MagicMock(return_value=call.body)
            res.info = MagicMock(return_value=info)
            res.headers = info
            res.code = call.status
            res.closed = False
            return res
        if call.error_data:
            res = MagicMock()
            res.closed = False
            body = call.error_data.get('body')
            if body is not None:
                res.read = MagicMock(return_value=body)
            else:
                res.read = MagicMock(side_effect=AttributeError('read'))
            raise HTTPError(url, call.status, 'Error', info, res)
        assert False, 'OpenUrlCall data has neither body nor error data'

    def assert_is_done(self):
        '''
        Assert that all expected ``open_url()`` calls have been made.
        '''
        assert self.index == len(self.calls), 'Got less open_url calls than expected (%d vs. %d)' % (self.index, len(self.calls))
