# Copyright (c) 2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import json
import sys
import traceback

from ansible.module_utils.common.text.converters import to_native

try:
    from urllib.parse import parse_qs
except ImportError:
    # Python 2.x fallback:
    from urlparse import parse_qs  # type: ignore

if sys.version_info[0] >= 3:
    import typing as t

    if t.TYPE_CHECKING:
        from collections.abc import Callable, Sequence


def _extract_query(url):
    # type: (str) -> dict[str, list[str]]
    query_index = url.find('?')
    fragment_index = url.find('#')
    if query_index > fragment_index and fragment_index > 0:
        query_index = -1
    if query_index < 0:
        return {}
    if fragment_index > 0:
        query = url[query_index + 1:fragment_index]
    else:
        query = url[query_index + 1:]
    return parse_qs(query, keep_blank_values=True)


def _reduce_url(url, remove_query=False, remove_fragment=False):
    # type: (str, bool, bool) -> str
    fragment_index = url.find('#')
    if remove_fragment and fragment_index > 0:
        url = url[:fragment_index]
        fragment_index = -1
    if remove_query:
        query_index = url.find('?')
        if query_index > fragment_index and fragment_index > 0:
            query_index = -1
        if query_index > 0:
            if fragment_index > 0:
                url = url[:query_index] + url[fragment_index:]
            else:
                url = url[:query_index]
    return url


class CallBase(object):
    '''
    Describes one call to ``fetch_url`` or ``open_url``.

    This class contains information on what ``fetch_url()`` or ``open_url()`` should return,
    and how to validate the data passed to it.
    '''

    def __init__(self, method, status):
        # type: (str, int) -> None
        '''
        Create an expected call. Must be passed information on the expected
        HTTP method and the HTTP status returned by the call.
        '''
        assert method == method.upper(), \
            'HTTP method names are case-sensitive and should be upper-case (RFCs 7230 and 7231)'
        self.method = method
        self.status = status
        self.body = None  # type: bytes | None
        self.headers = {}  # type: dict[str, str]
        self.error_data = {}  # type: dict[str, t.Any]
        self.expected_url = None  # type: str | None
        self.expected_url_without_query = False
        self.expected_url_without_fragment = False
        self.expected_headers = {}  # type: dict[str, str | None]
        self.expected_query = {}  # type: dict[str, list[str]]
        self.expected_content = None  # type: str | bytes | None
        self.expected_content_predicate = None  # type: Callable[[str | bytes | None], bool] | None
        self.form_parse = False
        self.form_present = set()  # type: set[str]
        self.form_values = {}  # type: dict[str, list[str]]
        self.json_parse = False
        self.json_present = set()  # type: set[tuple[str | int, ...]]
        self.json_absent = set()  # type: set[tuple[str | int, ...]]
        self.json_values = {}  # type: dict[tuple[str | int, ...], t.Any]
        self.timeout = None  # type: int | float | None
        self.basic_auth = None  # type: tuple[str, str] | None
        self.force_basic_auth = None  # type: bool | None

    def result(self, body):
        # type: (bytes) -> t.Self
        '''
        Builder method to set return body of the call. Must be a bytes string.
        '''
        self.body = body
        assert self.error_data.get('body') is None, 'Error body must not be given'
        return self

    def result_str(self, str_body):
        # type: (str) -> t.Self
        '''
        Builder method to set return body of the call as a text string.
        '''
        return self.result(str_body.encode('utf-8'))

    def result_json(self, json_body):
        # type: (t.Any) -> t.Self
        '''
        Builder method to set return body of the call as a JSON object.
        '''
        return self.result(json.dumps(json_body).encode('utf-8'))

    def expect_url(self, url, without_query=False, without_fragment=False):
        # type: (str, bool, bool) -> t.Self
        '''
        Builder method to set the expected URL for the call.
        '''
        self.expected_url = url
        self.expected_url_without_query = without_query
        self.expected_url_without_fragment = without_fragment
        return self

    def expect_query_values(self, parameter, *values):
        # type: (str, *str) -> t.Self
        '''
        Builder method to set an expected query parameter for the call.
        '''
        self.expected_query[parameter] = list(values)
        return self

    def return_header(self, name, value):
        # type: (str, str) -> t.Self
        '''
        Builder method to set a returned header for the call.
        '''
        assert value is not None
        self.headers[name] = value
        return self

    def expect_header(self, name, value):
        # type: (str, str) -> t.Self
        '''
        Builder method to set an expected header value for a call.
        '''
        self.expected_headers[name] = value
        return self

    def expect_header_unset(self, name):
        # type: (str) -> t.Self
        '''
        Builder method to set an expected non-set header for a call.
        '''
        self.expected_headers[name] = None
        return self

    def expect_content(self, content):
        # type: (str | bytes) -> t.Self
        '''
        Builder method to set an expected content for a call.
        '''
        self.expected_content = content
        return self

    def expect_content_predicate(self, content_predicate):
        # type: (Callable[[str | bytes | None], bool]) -> t.Self
        '''
        Builder method to set an expected content predicate for a call.
        '''
        self.expected_content_predicate = content_predicate
        return self

    def expect_form_present(self, key):
        # type: (str) -> t.Self
        '''
        Builder method to set an expected form field for a call.
        '''
        assert not self.json_parse
        self.form_parse = True
        self.form_present.add(key)
        return self

    def expect_form_values(self, key, values):
        # type: (str, list[str]) -> t.Self
        '''
        Builder method to set an expected form value for a call.
        '''
        assert not self.json_parse
        assert isinstance(values, list)
        self.form_parse = True
        self.form_values[key] = values
        return self

    def expect_form_value(self, key, value):
        # type: (str, str) -> t.Self
        '''
        Builder method to set an expected form value for a call.
        '''
        assert not self.json_parse
        self.form_parse = True
        self.form_values[key] = [value]
        return self

    def expect_form_value_absent(self, key):
        # type: (str) -> t.Self
        '''
        Builder method to set an expectedly absent form field for a call.
        '''
        assert not self.json_parse
        self.form_parse = True
        self.form_values[key] = []
        return self

    def expect_json_present(self, key):
        # type: (Sequence[str | int]) -> t.Self
        '''
        Builder method to set an expected JSON field for a call.
        The key must be a sequence: strings denote fields in objects, integers denote array indices.
        '''
        assert not self.form_parse
        self.json_parse = True
        self.json_present.add(tuple(key))
        return self

    def expect_json_value(self, key, value):
        # type: (Sequence[str | int], t.Any) -> t.Self
        '''
        Builder method to set an expected JSON value for a call.
        The key must be a sequence: strings denote fields in objects, integers denote array indices.
        '''
        assert not self.form_parse
        self.json_parse = True
        self.json_values[tuple(key)] = value
        return self

    def expect_json_value_absent(self, key):
        # type: (Sequence[str | int]) -> t.Self
        '''
        Builder method to set an expectedly absent JSON field for a call.
        The key must be a sequence: strings denote fields in objects, integers denote array indices.
        '''
        assert not self.form_parse
        self.json_parse = True
        self.json_absent.add(tuple(key))
        return self

    def expect_timeout(self, timeout):
        # type: (int | float) -> t.Self
        '''
        Builder method to set an expected timeout for a call.
        '''
        self.timeout = timeout
        return self

    def expect_basic_auth(self, username, password):
        # type: (str, str) -> t.Self
        '''
        Builder method to set expected basic authentication credentials for a call.
        '''
        self.basic_auth = (username, password)
        return self

    def expect_force_basic_auth(self, force):
        # type: (bool) -> t.Self
        '''
        Builder method to set force_basic_auth for a call.
        '''
        self.force_basic_auth = force
        return self


def _validate_form(call, data):
    # type: (CallBase, bytes | str | None) -> None
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
            assert form[k] == v, 'Form key "{0}" has not values {1!r}, but {2!r}'.format(k, v, form[k])


def _format_json_key(key):
    # type: (tuple[str | int, ...] | list[str | int]) -> str
    result = []
    first = True
    for k in key:
        if isinstance(k, int):
            result.append('[{0}]'.format(k))
        else:
            if not first:
                result.append('.')
            result.append(k)
        first = False
    return ''.join(result)


def _descend_json(data, key):
    # type: (t.Any, tuple[str | int, ...] | list[str | int]) -> tuple[t.Any, bool]
    if not key:
        return data, True
    for index, k in enumerate(key[:-1]):
        if isinstance(k, int):
            if not isinstance(data, (list, tuple)):
                raise AssertionError('Cannot resolve JSON key {0} in data: not a list on last level'.format(_format_json_key(key[:index + 1])))
            if k < 0 or k >= len(data):
                raise AssertionError('Cannot find JSON key {0} in data: index out of bounds'.format(_format_json_key(key[:index + 1])))
        else:
            if not isinstance(data, dict):
                raise AssertionError('Cannot resolve JSON key {0} in data: not a dictionary on last level'.format(_format_json_key(key[:index + 1])))
            if k not in data:
                raise AssertionError('Cannot find JSON key {0} in data: key not present'.format(_format_json_key(key[:index + 1])))
        data = data[k]
    if isinstance(key[-1], int):
        if not isinstance(data, (list, tuple)):
            raise AssertionError('Cannot resolve JSON key {0} in data: not a list on last level'.format(_format_json_key(key)))
        if key[-1] < 0 or key[-1] >= len(data):
            return None, False
    else:
        if not isinstance(data, dict):
            raise AssertionError('Cannot resolve JSON key {0} in data: not a dictionary on last level'.format(_format_json_key(key)))
        if key[-1] not in data:
            return None, False
    return data[key[-1]], True


def _validate_json(call, data):
    # type: (CallBase, str | bytes) -> None
    '''
    Validate JSON contents.
    '''
    data = json.loads(to_native(data))
    for k in call.json_present:
        dummy, present = _descend_json(data, k)
        assert present, 'JSON key {0} not present'.format(_format_json_key(k))
    for k in call.json_absent:
        dummy, present = _descend_json(data, k)
        assert not present, 'JSON key {0} present'.format(_format_json_key(k))
    for k, v in call.json_values.items():
        value, present = _descend_json(data, k)
        assert present, 'JSON key "{0}" not present'.format(_format_json_key(k))
        assert value == v, 'JSON key "{0}" has not value {1!r}, but {2!r}'.format(_format_json_key(k), v, value)


def _validate_query(call, url):
    # type: (CallBase, str) -> None
    '''
    Validate query parameters of a call.
    '''
    query = _extract_query(url)
    for k, v in call.expected_query.items():
        if k not in query:
            assert query.get(k) == v, 'Query parameter "{0}" not specified for call'.format(k)
        else:
            assert query.get(k) == v, \
                'Query parameter "{0}" specified for call, but with wrong value ({1!r} instead of {2!r})'.format(
                    k, query.get(k), v)


def _validate_headers(call, headers):
    # type: (CallBase, dict[str, str] | None) -> None
    '''
    Validate headers of a call.
    '''
    given_headers = {}
    if headers is not None:
        for k, v in headers.items():
            given_headers[k.lower()] = v
    for k, ev in call.expected_headers.items():
        if ev is None:
            assert k.lower() not in given_headers, 'Header "{0}" specified for call, but should not be'.format(k)
        else:
            assert given_headers.get(k.lower()) == ev, \
                'Header "{0}" specified for call, but with wrong value ({1!r} instead of {2!r})'.format(
                    k, given_headers.get(k.lower()), ev)


def validate_call(
    call,  # type: CallBase
    method,  # type: str | None
    url,  # type: str
    headers,  # type: dict[str, str] | None
    data,  # type: str | bytes | None
    timeout=10,  # type: int | float
    url_username=None,  # type: str | None
    url_password=None,  # type: str | None
    force_basic_auth=None,  # type: bool | None
):
    # type: (...) -> None
    method = method or 'GET'
    assert method == call.method, 'Expected method does not match for call: {0!r} instead of {1!r}'.format(
        method, call.method)
    if call.expected_url is not None:
        reduced_url = _reduce_url(
            url,
            remove_query=call.expected_url_without_query,
            remove_fragment=call.expected_url_without_fragment)
        assert reduced_url == call.expected_url, \
            'Expected URL does not match for call: {0!r} instead of {1!r}'.format(reduced_url, call.expected_url)
    if call.timeout is not None:
        assert timeout == call.timeout, \
            'Expected timeout does not match for call: {0!r} instead of {1!r}'.format(timeout, call.timeout)
    if call.basic_auth is not None:
        assert url_username == call.basic_auth[0], \
            'Expected url_username does not match for call: {0!r} instead of {1!r}'.format(url_username, call.basic_auth[0])
        assert url_password == call.basic_auth[1], \
            'Expected url_password does not match for call: {0!r} instead of {1!r}'.format(url_password, call.basic_auth[1])
    if call.force_basic_auth is not None:
        assert force_basic_auth == call.force_basic_auth, \
            'Expected force_basic_auth does not match for call: {0!r} instead of {1!r}'.format(force_basic_auth, call.force_basic_auth)
    if call.expected_query:
        _validate_query(call, url)
    if call.expected_headers:
        _validate_headers(call, headers)
    if call.expected_content is not None:
        assert data == call.expected_content, 'Expected content does not match for call: {0!r} instead of {1!r}'.format(
            data, call.expected_content)
    if call.expected_content_predicate:
        try:
            assert call.expected_content_predicate(data), 'Predicate has falsy result'
        except Exception as e:  # pragma: no cover
            raise AssertionError(  # pragma: no cover
                'Content does not match predicate for call: {0}\n\n{1}'.format(
                    e, traceback.format_exc()))
    if call.form_parse:
        _validate_form(call, data)
    if call.json_parse:
        assert data is not None, "Data must be provided"
        _validate_json(call, data)
