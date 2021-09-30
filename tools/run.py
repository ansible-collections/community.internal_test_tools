#!/usr/bin/env python

# Copyright: (c) 2020, Felix Fontein <felix@fontein.de>
# Copyright: (c) the ansible-test contributors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import argparse
import datetime
import errno
import json
import os
import random
import subprocess
import sys


COLORS = {
    'emph': 1,
    'gray': 37,
    'black': 30,
    'white': 97,
    'green': 32,
    'red': 31,
    'yellow': 33,
}


def colorize(text, color, use_color=True):
    if not use_color:
        return text
    color_id = COLORS.get(color)
    if color_id is None:
        return text
    return '\x1b[{0}m{1}\x1b[0m'.format(color_id, text)


def run(command, catch_output=False, use_color=True):
    sys.stdout.write(colorize('[RUN] {0}\n'.format(' '.join(command)), 'emph', use_color))
    sys.stdout.flush()
    if not catch_output:
        return subprocess.call(command), None, None
    process_result = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process_result.communicate()
    return process_result.returncode, stdout, stderr


def get_common_parent(*directories):
    parent = directories[0]
    for directory in directories[1:]:
        while os.path.relpath(directory, parent).startswith('..'):
            old_parent, parent = parent, os.path.dirname(parent)
            if old_parent == parent:
                break
    return parent


def get_default_container(use_color=True):
    try:
        try:
            # ansible-core 2.12
            from ansible_test._internal.completion import DOCKER_COMPLETION

            return DOCKER_COMPLETION['default'].image
        except ImportError:
            # ansible-core < 2.12
            try:
                from ansible_test._internal.util_common import docker_qualify_image
            except ImportError:
                from ansible_test._internal.util import docker_qualify_image

            image = docker_qualify_image('default')
            if not image:
                print(colorize('WARNING: cannot load default docker container version from ansible-test: default image not known', 'red', use_color))
            return image
    except Exception as exc:
        print(colorize('WARNING: cannot load default docker container version from ansible-test: {0}'.format(exc), 'red', use_color))
    return 'quay.io/ansible/default-test-container:4.0.1'


def pull_docker_image(image_name, use_color=True):
    for tries in range(3):
        rc, dummy, dummy = run(['docker', 'pull', image_name], use_color=use_color)
        if rc == 0:
            return
        print(colorize('WARNING: pulling docker image failed, retrying...', 'red', use_color))
    print(colorize('FATAL ERROR while pulling docker image', 'red', use_color))
    sys.exit(-1)


def write_test_results(subdir, name, extension, content):
    output_dir = os.path.join('tests', 'output', subdir)
    try:
        os.makedirs(output_dir.encode('utf-8'))
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            raise
    filename = os.path.join(output_dir, 'ansible-test-extra-%s.%s' % (name, extension))
    # print('Writing {0}...'.format(filename))
    with open(filename, 'wb') as file_obj:
        file_obj.write(content.encode('utf-8'))


def format_data(test, data):
    reason = 'an unknown error. Please check out the CI logs.'
    lines = []
    if 'errors' in data:
        if len(data['errors']) == 1:
            reason = '1 error:'
        else:
            reason = '%d errors:' % len(data['errors'])
        lines = ['{0}:{1}:{2}:{3}'.format(*error) for error in data['errors']]
    return 'The test `%s` failed with %s' % (test, reason), lines


def write_bot_data(test, data):
    message, lines = format_data(test, data)
    bot_data = dict(
        verified=True,
        docs='',  # URL describing tests
        results=[
            dict(
                message=message,
                output='\n'.join(lines),
            ),
        ],
    )
    content = json.dumps(
        bot_data,
        sort_keys=True,
        indent=4,
        separators=(', ', ': '),
    ) + '\n'
    write_test_results('bot', test, 'json', content)


def write_junit_data(test, data, junit):
    test_case = junit.TestCase(classname=test.title().replace('-', ''), name=test)
    message, lines = format_data(test, data)
    test_case.add_failure_info(message=message, output='\n%s' % '\n'.join(lines))
    test_suites = [
        junit.TestSuite(
            name='extra-sanity',
            test_cases=[test_case],
            timestamp=datetime.datetime.utcnow().replace(microsecond=0).isoformat(),
        ),
    ]
    # the junit_xml API is changing in version 2.0.0
    # TestSuite.to_xml_string is being replaced with to_xml_report_string
    # see: https://github.com/kyrus/python-junit-xml/blob/63db26da353790500642fd02cae1543eb41aab8b/junit_xml/__init__.py#L249-L261
    try:
        to_xml_string = junit.to_xml_report_string
    except AttributeError:
        # noinspection PyDeprecation
        to_xml_string = junit.TestSuite.to_xml_string

    report = to_xml_string(test_suites=test_suites, prettyprint=True, encoding='utf-8')

    write_test_results('junit', test, 'xml', report)


def main():
    parser = argparse.ArgumentParser(description='Extra sanity test runner.')
    parser.add_argument('--color',
                        action='store_true',
                        help='use ANSI colors')
    parser.add_argument('--docker-no-pull',
                        action='store_true',
                        help='do not try to pull the docker image')
    parser.add_argument('--bot',
                        action='store_true',
                        help='store error results as JSON for ansibullbot')
    parser.add_argument('--junit',
                        action='store_true',
                        help='store error results as JUnit for AZP')
    parser.add_argument('targets',
                        metavar='TARGET',
                        nargs='*',
                        help='targets')

    args = parser.parse_args()

    use_color = sys.stdout.isatty()
    if args.color:
        use_color = True

    junit = None
    if args.junit:
        try:
            import junit_xml as junit
        except ImportError as exc:
            print(colorize('FATAL ERROR during importing junit_xml: {0}'.format(exc), 'emph', use_color))
            sys.exit(-1)

    cwd = os.getcwd()
    root = cwd
    my_dir = '.'
    try:
        my_dir = os.path.dirname(__file__)
        root = get_common_parent(root, my_dir)
    except Exception:  # pylint: disable=broad-except
        pass

    targets = list(args.targets)

    container_name = 'ansible-test-{0}'.format(random.getrandbits(64))
    output_filename = 'output-{0}.json'.format(random.getrandbits(32))

    image_name = get_default_container(use_color=use_color)
    if not args.docker_no_pull:
        pull_docker_image(image_name, use_color=use_color)

    result = None
    run([
        'docker', 'run', '--detach',
        '--workdir', os.path.abspath(cwd),
        '--name', container_name,
        image_name,
        '/bin/sh', '-c', 'sleep 50m',
    ], use_color=use_color)
    try:
        run(['docker', 'cp', root, '{0}:{1}'.format(container_name, os.path.dirname(root))], use_color=use_color)
        # run(['docker', 'exec', container_name, '/bin/sh', '-c', 'ls -lah ; pwd'])
        command = ['docker', 'exec', container_name]
        command.extend(['python3.8', os.path.relpath(os.path.join(my_dir, 'runner.py'), cwd)])
        command.extend(['--cleanup', '--install-requirements', '--output', output_filename])
        if use_color:
            command.extend(['--color'])
        command.extend(targets)
        run(command, use_color=use_color)
        dummy, result, stderr = run(['docker', 'exec', container_name, 'cat', output_filename], catch_output=True, use_color=use_color)
        if stderr:
            print(colorize('WARNING: {0}'.format(stderr.decode('utf-8').strip()), 'emph', use_color))
    except Exception as exc:  # pylint: disable=broad-except
        print(colorize('FATAL ERROR during execution: {0}'.format(exc), 'emph', use_color))
    finally:
        try:
            run(['docker', 'rm', '-f', container_name], use_color=use_color)
        except Exception as exc:  # pylint: disable=broad-except
            print(colorize('ERROR while removing docker container: {0}'.format(exc), 'emph', use_color))
    if result is None:
        sys.exit(-1)

    try:
        result = json.loads(result.decode('utf-8'))
    except Exception as exc:  # pylint: disable=broad-except
        print(colorize('FATAL ERROR while receiving output: {0}'.format(exc), 'red', use_color))
        sys.exit(-1)

    failed_tests = []
    total_errors = 0
    for test, data in result.items():
        if data.get('skipped'):
            continue
        if not data['success']:
            failed_tests.append(test)
            if 'errors' in data:
                total_errors += len(data['errors'])
            if args.bot:
                write_bot_data(test, data)
            if junit:
                write_junit_data(test, data, junit)
    if total_errors or failed_tests:
        print(colorize('Total of {0} errors in the following {1} tests (out of {2}):'.format(total_errors, len(failed_tests), len(result)), 'emph', use_color))
        for test in sorted(failed_tests):
            print(colorize(test, 'red', use_color))
        sys.exit(-1)
    else:
        print(colorize('Success.', 'green', use_color))
        sys.exit(0)


if __name__ == '__main__':
    main()
