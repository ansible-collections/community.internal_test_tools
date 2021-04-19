# (c) 2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import pytest

from ansible_collections.community.internal_test_tools.tests.unit.utils._utils import (
    CallBase,
    _extract_query,
    _reduce_url,
    _validate_form,
    _format_json_key,
    _descend_json,
    _validate_json,
    _validate_query,
    _validate_headers,
)


def test_extract_query():
    assert _extract_query('a?b#c') == {'b': ['']}
    assert _extract_query('a#c') == {}
    assert _extract_query('a#c?b') == {}
    assert _extract_query('a?b=1&b=2#c') == {'b': ['1', '2']}
    assert _extract_query('a?b=1&a=3?b=2&a=4#c') == {'b': ['1'], 'a': ['3?b=2', '4']}
    assert _extract_query('a?b=1&a=3&b=2&a=4#c') == {'b': ['1', '2'], 'a': ['3', '4']}


def test_reduce_url():
    assert _reduce_url('a?b#c') == 'a?b#c'
    assert _reduce_url('a?b#c', remove_query=True) == 'a#c'
    assert _reduce_url('a?b#c', remove_fragment=True) == 'a?b'
    assert _reduce_url('a?b#c', remove_query=True, remove_fragment=True) == 'a'
    assert _reduce_url('a#c?b') == 'a#c?b'
    assert _reduce_url('a#c?b', remove_query=True) == 'a#c?b'
    assert _reduce_url('a#c?b', remove_fragment=True) == 'a'
    assert _reduce_url('a#c?b', remove_query=True, remove_fragment=True) == 'a'
    assert _reduce_url('a', remove_query=True) == 'a'
    assert _reduce_url('a#c', remove_query=True) == 'a#c'
    assert _reduce_url('a?b', remove_fragment=True) == 'a?b'


def test_validate_form():
    _validate_form(
        CallBase('GET', 200)
        .expect_form_present('a')
        .expect_form_value('c', 'd')
        .expect_form_value_absent('b'),
        'a=b&c=d')
    with pytest.raises(AssertionError):
        assert _validate_form(CallBase('GET', 200).expect_form_value('c', 'd'), 'c=d&c=e')
    with pytest.raises(AssertionError):
        assert _validate_form(CallBase('GET', 200).expect_form_present('a'), 'c=d')
    with pytest.raises(AssertionError):
        assert _validate_form(CallBase('GET', 200).expect_form_value('c', 'a'), 'c=d')
    with pytest.raises(AssertionError):
        assert _validate_form(CallBase('GET', 200).expect_form_value_absent('c'), 'c=d')


def test_format_json_key():
    assert _format_json_key([]) == ''
    assert _format_json_key(['a']) == 'a'
    assert _format_json_key([1]) == '[1]'
    assert _format_json_key(['a', 1]) == 'a[1]'
    assert _format_json_key(['a', 1, 'b']) == 'a[1].b'
    assert _format_json_key(['a', 'b', 'c', 3]) == 'a.b.c[3]'


def test_descend_json():
    assert _descend_json('foo', []) == ('foo', True)
    assert _descend_json({}, []) == ({}, True)
    assert _descend_json({}, ['a']) == (None, False)
    assert _descend_json({'a': 1}, ['a']) == (1, True)
    assert _descend_json({'a': None}, ['a']) == (None, True)
    assert _descend_json({'a': ['b']}, ['a', 0]) == ('b', True)
    assert _descend_json({'a': ['b']}, ['a', -1]) == (None, False)
    assert _descend_json({'a': ['b']}, ['a', 1]) == (None, False)
    assert _descend_json({'a': [{'b': 'c'}]}, ['a', 0, 'b']) == ('c', True)
    # Middle
    with pytest.raises(AssertionError):
        _descend_json([], ['a', 0])
    with pytest.raises(AssertionError):
        _descend_json([], [0, 0])
    with pytest.raises(AssertionError):
        _descend_json('foo', ['a', 0])
    with pytest.raises(AssertionError):
        _descend_json({}, [0, 0])
    with pytest.raises(AssertionError):
        _descend_json({}, ['a', 0])
    with pytest.raises(AssertionError):
        _descend_json('foo', [0, 0])
    # End
    with pytest.raises(AssertionError):
        _descend_json([], ['a'])
    with pytest.raises(AssertionError):
        _descend_json('foo', ['a'])
    with pytest.raises(AssertionError):
        _descend_json({}, [0])
    with pytest.raises(AssertionError):
        _descend_json('foo', [0])


def test_validate_json():
    _validate_json(
        CallBase('GET', 200)
        .expect_json_present(['a'])
        .expect_json_value(['c'], 'd')
        .expect_json_value_absent(['b']),
        '{"a": "b", "c": "d"}')
    _validate_json(
        CallBase('GET', 200)
        .expect_json_present([0])
        .expect_json_value([1], 'd')
        .expect_json_value_absent([2]),
        '["a", "d"]')
    with pytest.raises(AssertionError):
        assert _validate_json(CallBase('GET', 200).expect_json_present(['a']), '{"c":"d"}')
    with pytest.raises(AssertionError):
        assert _validate_json(CallBase('GET', 200).expect_json_value(['c'], 'a'), '{"c":"d"}')
    with pytest.raises(AssertionError):
        assert _validate_json(CallBase('GET', 200).expect_json_value_absent(['c']), '{"c":"d"}')


def test_validate_query():
    _validate_query(
        CallBase('GET', 200)
        .expect_query_values('b', 'c', 'd')
        .expect_query_values('e', 'f'),
        'a?b=c&b=d&e=f')
    with pytest.raises(AssertionError):
        assert _validate_query(CallBase('GET', 200).expect_query_values('a'), 'a?b=c&b=d&e=f')
    with pytest.raises(AssertionError):
        assert _validate_query(CallBase('GET', 200).expect_query_values('b', 'e'), 'a?b=c&b=d&e=f')


def test_validate_headers():
    _validate_headers(
        CallBase('GET', 200)
        .expect_header('content-type', 'foo')
        .expect_header('Content-type', 'foo')
        .expect_header('bar', 'baz')
        .expect_header_unset('baz')
        .expect_header_unset('test'),
        {
            'Content-Type': 'foo',
            'bar': 'baz',
        })
    with pytest.raises(AssertionError):
        assert _validate_headers(CallBase('GET', 200).expect_header('foo', 'bar'), {})
    with pytest.raises(AssertionError):
        assert _validate_headers(CallBase('GET', 200).expect_header('foo', 'bar'), {'foo': 'baz'})
    with pytest.raises(AssertionError):
        assert _validate_headers(CallBase('GET', 200).expect_header('foo', 'bar'), {'foo': 'BAR'})
    with pytest.raises(AssertionError):
        assert _validate_headers(CallBase('GET', 200).expect_header_unset('foo'), {'foo': 'bar'})
    with pytest.raises(AssertionError):
        assert _validate_headers(CallBase('GET', 200).expect_header_unset('foo'), {'Foo': 'bar'})
