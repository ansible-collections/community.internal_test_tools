#!/usr/bin/env python

# Copyright (c) 2020, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import argparse
import os
import sys

# Make sure that our collection root is in the Python package search path
# This makes it possible to import `tools.lib.xxx` no matter whether this
# script was invoked by `python -m tools.xxx` or by `tools/xxx.py`.
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tools.lib.ansible import PLUGIN_TYPES
from tools.lib.meta_runtime import (
    extract_meta_redirects,
    load_ansible_core_runtime,
    scan_file_redirects,
    scan_plugins,
)
from tools.lib.yaml import load_yaml


GALAXY_PATH = 'galaxy.yml'
RUNTIME_PATH = 'meta/runtime.yml'


def func_check_ansible_core_redirects(args):
    collection_root = args.collection_root
    galaxy_path = os.path.join(collection_root, GALAXY_PATH)
    runtime_path = os.path.join(collection_root, RUNTIME_PATH)

    if not os.path.exists(galaxy_path):
        raise Exception("The collection root must point to a collection's root directory, that contains galaxy.yml.")

    # Load basic information on collection
    galaxy = load_yaml(galaxy_path)
    collection_name = '{namespace}.{name}'.format(**galaxy)
    print('Working on collection {name}'.format(name=collection_name))

    # Load meta/runtime
    if os.path.exists(os.path.join(collection_root, runtime_path)):
        runtime = load_yaml(runtime_path)
    else:
        runtime = None

    if not runtime:
        runtime = dict()

    ansible_builtin_runtime = load_ansible_core_runtime()

    # Collect all redirects and plugins
    redirects = dict()
    plugins = dict()
    for plugin_type in PLUGIN_TYPES:
        redirects[plugin_type] = dict()
        plugins[plugin_type] = set()

    scan_file_redirects(redirects, collection_root=collection_root)
    extract_meta_redirects(redirects, runtime, collection_name)

    scan_plugins(plugins, redirects, runtime, collection_root=collection_root)

    # Check ansible.builtin's runtime against what we have
    collection_prefix = '{collection_name}.'.format(collection_name=collection_name)
    for plugin_type in PLUGIN_TYPES:
        our_plugins = plugins[plugin_type]
        ansible_builtin_redirects = ansible_builtin_runtime['plugin_routing'].get(plugin_type)
        if ansible_builtin_redirects:
            for plugin_name, plugin_data in ansible_builtin_redirects.items():
                if 'redirect' in plugin_data:
                    if plugin_data['redirect'].startswith(collection_prefix):
                        redirect_name = plugin_data['redirect'][len(collection_prefix):]
                        if redirect_name not in our_plugins:
                            print(
                                'ERROR: ansible-core {plugin_type} {plugin_name} redirects to '
                                '{collection_name}.{redirect_name}, which does not exist!'.format(
                                    plugin_type=plugin_type,
                                    plugin_name=plugin_name,
                                    collection_name=collection_name,
                                    redirect_name=redirect_name,
                                ))
                    elif plugin_name in our_plugins:
                        print(
                            'WARNING: ansible-core {plugin_type} {plugin_name} redirects to '
                            '{redirect_fqcn} and not to ours!'.format(
                                plugin_type=plugin_type,
                                plugin_name=plugin_name,
                                redirect_fqcn=plugin_data['redirect'],
                            ))


def func_show_redirects_inventory(args):
    ansible_builtin_runtime = load_ansible_core_runtime()

    collections = set()
    for plugin_type, entries in ansible_builtin_runtime['plugin_routing'].items():
        for plugin_name, entry in entries.items():
            if 'redirect' in entry:
                namespace, collection = entry['redirect'].split('.', 2)[:2]
                collections.add('{namespace}.{collection}'.format(
                    namespace=namespace,
                    collection=collection,
                ))

    for collection in sorted(collections):
        print(collection)


def main():
    parser = argparse.ArgumentParser(description='meta/runtime.yml helper')

    subparsers = parser.add_subparsers(metavar='COMMAND')

    check_ansible_core_redirects_parser = subparsers.add_parser('check-ansible-core-redirects',
                                                                help='Compare current collection to redirects in '
                                                                     'ansible-core (needs to be installed)')
    check_ansible_core_redirects_parser.set_defaults(func=func_check_ansible_core_redirects)
    check_ansible_core_redirects_parser.add_argument('--collection-root', default='.',
                                                     help='The root directory of the collection to analyze')

    ansible_core_redirects_inventory_parser = subparsers.add_parser('show-redirects-inventory',
                                                                    help='List all collections that '
                                                                         'ansible-core (needs to be '
                                                                         'installed) redirects to in its '
                                                                         'ansible_builtin_runtime.yml')
    ansible_core_redirects_inventory_parser.set_defaults(func=func_show_redirects_inventory)

    args = parser.parse_args()

    if getattr(args, 'func', None) is None:
        parser.print_help()
        return 2

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
