# (c) 2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import json
import traceback

from ansible.module_utils._text import to_native
from ansible.module_utils.six.moves.urllib.parse import parse_qs


def _extract_query(url):
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
        '''
        Create an expected call. Must be passed information on the expected
        HTTP method and the HTTP status returned by the call.
        '''
        assert method == method.upper(), \
            'HTTP method names are case-sensitive and should be upper-case (RFCs 7230 and 7231)'
        self.method = method
        self.status = status
        self.body = None
        self.headers = {}
        self.error_data = {}
        self.expected_url = None
        self.expected_url_without_query = False
        self.expected_url_without_fragment = False
        self.expected_headers = {}
        self.expected_query = {}
        self.expected_content = None
        self.expected_content_predicate = None
        self.form_parse = False
        self.form_present = set()
        self.form_values = {}
        self.form_values_one = {}
        self.json_parse = False
        self.json_present = set()
        self.json_absent = set()
        self.json_values = {}

    def result(self, body):
        '''
        Builder method to set return body of the call. Must be a bytes string.
        '''
        self.body = body
        assert self.error_data.get('body') is None, 'Error body must not be given'
        return self

    def result_str(self, str_body):
        '''
        Builder method to set return body of the call as a text string.
        '''
        return self.result(str_body.encode('utf-8'))

    def result_json(self, json_body):
        '''
        Builder method to set return body of the call as a JSON object.
        '''
        return self.result(json.dumps(json_body).encode('utf-8'))

    def result_error(self, msg, body=None):
        '''
        Builder method to set return body of the call in case of an error.
        '''
        self.error_data['msg'] = msg
        if body is not None:
            self.error_data['body'] = body
            assert self.body is None, 'Result must not be given if error body is provided'
        return self

    def expect_url(self, url, without_query=False, without_fragment=False):
        '''
        Builder method to set the expected URL for the call.
        '''
        self.expected_url = url
        self.expected_url_without_query = without_query
        self.expected_url_without_fragment = without_fragment
        return self

    def expect_query_values(self, parameter, *values):
        '''
        Builder method to set an expected query parameter for the call.
        '''
        self.expected_query[parameter] = list(values)
        return self

    def return_header(self, name, value):
        '''
        Builder method to set a returned header for the call.
        '''
        assert value is not None
        self.headers[name] = value
        return self

    def expect_header(self, name, value):
        '''
        Builder method to set an expected header value for a call.
        '''
        self.expected_headers[name] = value
        return self

    def expect_header_unset(self, name):
        '''
        Builder method to set an expected non-set header for a call.
        '''
        self.expected_headers[name] = None
        return self

    def expect_content(self, content):
        '''
        Builder method to set an expected content for a call.
        '''
        self.expected_content = content
        return self

    def expect_content_predicate(self, content_predicate):
        '''
        Builder method to set an expected content predicate for a call.
        '''
        self.expected_content_predicate = content_predicate
        return self

    def expect_form_present(self, key):
        '''
        Builder method to set an expected form field for a call.
        '''
        assert not self.json_parse
        self.form_parse = True
        self.form_present.add(key)
        return self

    def expect_form_value(self, key, value):
        '''
        Builder method to set an expected form value for a call.
        '''
        assert not self.json_parse
        self.form_parse = True
        self.form_values[key] = [value]
        return self

    def expect_form_value_absent(self, key):
        '''
        Builder method to set an expectedly absent form field for a call.
        '''
        assert not self.json_parse
        self.form_parse = True
        self.form_values[key] = []
        return self

    def expect_json_present(self, key):
        '''
        Builder method to set an expected JSON field for a call.
        The key must be a sequence: strings denote fields in objects, integers denote array indices.
        '''
        assert not self.form_parse
        self.json_parse = True
        self.json_present.add(tuple(key))
        return self

    def expect_json_value(self, key, value):
        '''
        Builder method to set an expected JSON value for a call.
        The key must be a sequence: strings denote fields in objects, integers denote array indices.
        '''
        assert not self.form_parse
        self.json_parse = True
        self.json_values[tuple(key)] = value
        return self

    def expect_json_value_absent(self, key):
        '''
        Builder method to set an expectedly absent JSON field for a call.
        The key must be a sequence: strings denote fields in objects, integers denote array indices.
        '''
        assert not self.form_parse
        self.json_parse = True
        self.json_absent.add(tuple(key))
        return self


def _validate_form(call, data):
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


def _format_json_key(key):
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
    '''
    Validate headers of a call.
    '''
    given_headers = {}
    if headers is not None:
        for k, v in headers.items():
            given_headers[k.lower()] = v
    for k, v in call.expected_headers.items():
        if v is None:
            assert k.lower() not in given_headers, 'Header "{0}" specified for call, but should not be'.format(k)
        else:
            assert given_headers.get(k.lower()) == v, \
                'Header "{0}" specified for call, but with wrong value ({1!r} instead of {2!r})'.format(
                    k, given_headers.get(k.lower()), v)


def validate_call(call, method, url, headers, data):
    assert method == call.method, 'Expected method does not match for call: {0!r} instead of {1!r}'.format(
        method, call.method)
    if call.expected_url is not None:
        reduced_url = _reduce_url(
            url,
            remove_query=call.expected_url_without_query,
            remove_fragment=call.expected_url_without_fragment)
        assert reduced_url == call.expected_url, \
            'Expected URL does not match for call: {0!r} instead of {1!r}'.format(reduced_url, call.expected_url)
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
        except Exception as e:
            raise AssertionError(
                'Content does not match predicate for call: {0}\n\n{1}'.format(
                    e, traceback.format_exc()))
    if call.form_parse:
        _validate_form(call, data)
    if call.json_parse:
        _validate_json(call, data)
