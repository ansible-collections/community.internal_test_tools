# (c) 2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Small framework for testing modules and plugins which use ``open_url()`` from
``ansible.module_utils.urls`` to communicate with a HTTP service.

The main interface consists of the classes ``OpenUrlCall`` and
``OpenUrlProxy``.

Tests are expected to mock ``open_url`` with an instance of ``OpenUrlProxy``,
and to call its ``assert_is_done`` at the end of the test.

An example test could look as follows::

    import pytest

    from mock import MagicMock

    from ansible.inventory.data import InventoryData

    from ansible_collections.community.internal_test_tools.tests.unit.utils.open_url_framework import (
        OpenUrlCall,
        OpenUrlProxy,
    )

    from ansible_collections.community.hrobot.plugins.inventory.robot import InventoryModule
    from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL


    @pytest.fixture(scope="module")
    def inventory():
        r = InventoryModule()
        r.inventory = InventoryData()
        return r


    def get_option(option):
        if option == 'filters':
            return {}
        return False


    def test_populate(inventory, mocker):
        open_url = OpenUrlProxy([
            OpenUrlCall('GET', 200)
            .result_json([
                {
                    'server': {
                        'server_ip': '1.2.3.4',
                    },
                },
                {
                    'server': {
                        'server_ip': '1.2.3.5',
                        'server_name': 'test-server',
                    },
                },
            ])
            .expect_url('{0}/server'.format(BASE_URL)),
        ])
        mocker.patch('ansible_collections.community.hrobot.plugins.module_utils.robot.open_url', open_url)

        inventory.get_option = mocker.MagicMock(side_effect=get_option)
        inventory.populate(inventory.get_servers())

        open_url.assert_is_done()

        host_1 = inventory.inventory.get_host('1.2.3.4')
        host_2 = inventory.inventory.get_host('test-server')

This test makes sure that if the ``community.hrobot.robot`` inventory plugin's
get_servers() and populate() methods are called, one ``open_url()`` call is made
to ``GET`` the URL, and if this call is returned with a ``200 OK`` and the
given JSON object, that two hosts are added to the inventory.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import json

import pytest

from mock import MagicMock

from ansible.module_utils._text import to_native
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.six.moves.urllib.parse import parse_qs


class OpenUrlCall:
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
        assert method == method.upper(), \
            'HTTP method names are case-sensitive and should be upper-case (RFCs 7230 and 7231)'
        self.method = method
        self.status = status
        self.exception_generator = None
        self.body = None
        self.headers = {}
        self.error_data = {}
        self.expected_url = None
        self.expected_headers = {}
        self.form_parse = False
        self.form_present = set()
        self.form_values = {}
        self.form_values_one = {}

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
        self.body = body
        assert self.error_data.get('body') is None, 'Error body must not be given if body is provided'
        assert self.exception_generator is None, 'Exception generator must not be given if body is provided'
        return self

    def result_str(self, str_body):
        '''
        Builder method to set return body of the ``open_url()`` call as a text string.
        '''
        return self.result(str_body.encode('utf-8'))

    def result_json(self, json_body):
        '''
        Builder method to set return body of the ``open_url()`` call as a JSON object.
        '''
        return self.result(json.dumps(json_body).encode('utf-8'))

    def result_error(self, msg, body=None):
        '''
        Builder method to set return body of the ``open_url()`` call in case of an error.
        '''
        self.error_data['msg'] = msg
        if body is not None:
            self.error_data['body'] = body
            assert self.body is None, 'Result must not be given if error body is provided'
        assert self.exception_generator is None, 'Exception generator must not be given if error is provided'
        return self

    def expect_url(self, url):
        '''
        Builder method to set the expected URL for the ``open_url()`` call.
        '''
        self.expected_url = url
        return self

    def return_header(self, name, value):
        '''
        Builder method to set a returned header for the ``open_url()`` call.
        '''
        assert value is not None
        self.headers[name] = value
        return self

    def expect_header(self, name, value):
        '''
        Builder method to set an expected header value for a ``open_url()`` call.
        '''
        self.expected_headers[name] = value
        return self

    def expect_header_unset(self, name):
        '''
        Builder method to set an expected non-set header for a ``open_url()`` call.
        '''
        self.expected_headers[name] = None
        return self

    def expect_form_present(self, key):
        '''
        Builder method to set an expected form field for a ``open_url()`` call.
        '''
        self.form_parse = True
        self.form_present.add(key)
        return self

    def expect_form_value(self, key, value):
        '''
        Builder method to set an expected form value for a ``open_url()`` call.
        '''
        self.form_parse = True
        self.form_values[key] = [value]
        return self

    def expect_form_value_absent(self, key):
        '''
        Builder method to set an expectedly absent form field for a ``open_url()`` call.
        '''
        self.form_parse = True
        self.form_values[key] = []
        return self


class OpenUrlProxy:
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

    def _validate_form(self, call, data):
        '''
        Validate form contents.
        '''
        form = {}
        if data is not None:
            form = parse_qs(to_native(data), keep_blank_values=True)
        for k in call.form_present:
            assert k in form, 'Form key "{0}" not present'.format(k)
        for k, v in call.form_values.items():
            if len(v) == 0:
                assert k not in form, 'Form key "{0}" not absent'.format(k)
            else:
                assert form[k] == v, 'Form key "{0}" has not values {1}, but {2}'.format(k, v, form[k])
        for k, v in call.form_values_one.items():
            assert v <= set(form[k]), 'Form key "{0}" has values {2}, which does not include all of {1}'.format(k, v, form[k])

    def _validate_headers(self, call, headers):
        '''
        Validate headers of a call.
        '''
        given_headers = {}
        if headers is not None:
            for k, v in headers.items():
                given_headers[k.lower()] = v
        for k, v in call.expected_headers.items():
            if v is None:
                assert k.lower() not in given_headers, \
                    'Header "{0}" specified for open_url call, but should not be'.format(k)
            else:
                assert given_headers.get(k.lower()) == v, \
                    'Header "{0}" specified for fetch_url call, but with wrong value ({1!r} instead of {2!r})'.format(
                        k, given_headers.get(k.lower()), v)

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
        assert method == call.method
        if call.expected_url is not None:
            assert url == call.expected_url, \
                'Exepected URL does not match for open_url call'
        if call.expected_headers:
            self._validate_headers(call, headers)
        if call.form_parse:
            self._validate_form(call, data)

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
            return res
        if call.error_data:
            res = MagicMock()
            res.read = MagicMock(return_value=call.body)
            raise HTTPError(url, call.status, 'Error', info, res)
        assert False, 'OpenUrlCall data has neither body nor error data'

    def assert_is_done(self):
        '''
        Assert that all expected ``open_url()`` calls have been made.
        '''
        assert self.index == len(self.calls), 'Got less open_url calls than expected'
