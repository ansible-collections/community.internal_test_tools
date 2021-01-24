#!/usr/bin/env python

# Copyright: (c) 2020, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import argparse
import os
import sys

from lib.ansible import PLUGIN_TYPES
from lib.meta_runtime import (
    scan_file_redirects,
    extract_meta_redirects,
    scan_flatmap_redirects,
    sort_plugin_routing,
    add_meta_redirects,
    add_file_redirects,
    scan_plugins,
)
from lib.yaml import load_yaml, store_yaml


GALAXY_PATH = 'galaxy.yml'
RUNTIME_PATH = 'meta/runtime.yml'


def func_redirect(args):
    if args.target == 'meta':
        symlink_redirects = False
        meta_redirects = True
    elif args.target == 'symlinks':
        symlink_redirects = True
        meta_redirects = False
    elif args.target == 'both':
        symlink_redirects = True
        meta_redirects = True
    else:
        print('ERROR: Invalid value for "target". Must be one of "meta", "symlinks" or "both".')
        return 2

    # Load basic information on collection
    galaxy = load_yaml(GALAXY_PATH)
    collection_name = '{namespace}.{name}'.format(**galaxy)
    print('Working on collection {name}'.format(name=collection_name))

    # Load meta/runtime
    if os.path.exists(RUNTIME_PATH):
        runtime = load_yaml(RUNTIME_PATH)
    else:
        runtime = None

    if not runtime:
        runtime = dict()

    # Scan for wanted set of redirects
    redirects = dict()
    for plugin_type in PLUGIN_TYPES:
        redirects[plugin_type] = dict()

    scan_file_redirects(redirects)
    extract_meta_redirects(redirects, runtime, collection_name)

    # Scan flatmap redirects
    if args.flatmap:
        scan_flatmap_redirects(redirects)

    for plugin_type in PLUGIN_TYPES:
        if redirects[plugin_type]:
            print('Found {count} redirect{plural} for plugin type {type}'.format(
                count=len(redirects[plugin_type]),
                plural='s' if len(redirects[plugin_type]) != 1 else '',
                type=plugin_type))

    # Record result to disk
    if meta_redirects:
        add_meta_redirects(redirects, runtime, collection_name)
    else:
        extract_meta_redirects(redirects, runtime, collection_name, remove=True)
    if args.sort_plugin_routing:
        sort_plugin_routing(runtime)
    store_yaml(RUNTIME_PATH, runtime)

    if symlink_redirects:
        add_file_redirects(redirects)
    else:
        scan_file_redirects(redirects, remove=True)


def load_ansible_base_runtime():
    # Load ansible-base's ansible.builtin runtime
    from ansible import release as ansible_release

    ansible_builtin_runtime_path = os.path.join(
        os.path.dirname(ansible_release.__file__), 'config', 'ansible_builtin_runtime.yml')

    return load_yaml(ansible_builtin_runtime_path)


def func_check_ansible_base_redirects(args):
    # Load basic information on collection
    galaxy = load_yaml(GALAXY_PATH)
    collection_name = '{namespace}.{name}'.format(**galaxy)
    print('Working on collection {name}'.format(name=collection_name))

    # Load meta/runtime
    if os.path.exists(RUNTIME_PATH):
        runtime = load_yaml(RUNTIME_PATH)
    else:
        runtime = None

    if not runtime:
        runtime = dict()

    ansible_builtin_runtime = load_ansible_base_runtime()

    # Collect all redirects and plugins
    redirects = dict()
    plugins = dict()
    for plugin_type in PLUGIN_TYPES:
        redirects[plugin_type] = dict()
        plugins[plugin_type] = set()

    scan_file_redirects(redirects)
    extract_meta_redirects(redirects, runtime, collection_name)

    scan_plugins(plugins, redirects, runtime)

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
                                'ERROR: ansible-base {plugin_type} {plugin_name} redirects to '
                                '{collection_name}.{redirect_name}, which does not exist!'.format(
                                    plugin_type=plugin_type,
                                    plugin_name=plugin_name,
                                    collection_name=collection_name,
                                    redirect_name=redirect_name,
                                ))
                    elif plugin_name in our_plugins:
                        print(
                            'WARNING: ansible-base {plugin_type} {plugin_name} redirects to '
                            '{redirect_fqcn} and not to ours!'.format(
                                plugin_type=plugin_type,
                                plugin_name=plugin_name,
                                redirect_fqcn=plugin_data['redirect'],
                            ))


def func_ansible_base_redirects_inventory(args):
    ansible_builtin_runtime = load_ansible_base_runtime()

    collections = set()
    for plugin_type, entries in ansible_builtin_runtime['plugin_routing'].items():
        for plugin_name, entry in entries.items():
            if 'redirect' in entry:
                namespace, collection, name = entry['redirect'].split('.', 2)
                collections.add('{namespace}.{collection}'.format(
                    namespace=namespace,
                    collection=collection,
                ))

    for collection in sorted(collections):
        print(collection)


def func_validate(args):
    # Load basic information on collection
    galaxy = load_yaml(GALAXY_PATH)
    collection_name = '{namespace}.{name}'.format(**galaxy)
    print('Working on collection {name}'.format(name=collection_name))

    # Load meta/runtime
    if os.path.exists(RUNTIME_PATH):
        runtime = load_yaml(RUNTIME_PATH)
    else:
        runtime = None

    if not runtime:
        runtime = dict()

    ansible_builtin_runtime = load_ansible_base_runtime()

    # Collect all redirects and plugins
    redirects = dict()
    empty_redirects = dict()
    plugins = dict()
    for plugin_type in PLUGIN_TYPES:
        redirects[plugin_type] = dict()
        empty_redirects[plugin_type] = dict()
        plugins[plugin_type] = set()

    scan_file_redirects(redirects)
    extract_meta_redirects(redirects, runtime, collection_name)

    scan_plugins(plugins, empty_redirects, runtime, all_plugins=True)

    plugin_routing = runtime.get('plugin_routing') or dict()

    for plugin_type in PLUGIN_TYPES:
        our_plugins = plugins[plugin_type]
        our_redirects = redirects[plugin_type]

        missing = our_redirects.keys() - our_plugins
        while missing:
            found = False
            for plugin_name in list(missing):
                if our_redirects[plugin_name] in our_plugins:
                    our_plugins.add(plugin_name)
                    missing.remove(plugin_name)
                    found = True
            if not found:
                break

        if plugin_type in plugin_routing:
            for plugin_name, plugin_data in plugin_routing[plugin_type].items():
                if 'redirect' not in plugin_data and plugin_name not in our_plugins:
                    missing.add(plugin_name)

        if missing:
            print('{count} {plugin_type} plugin{plural} are missing:'.format(
                count=len(missing),
                plugin_type=plugin_type,
                plural='s' if len(missing) != 1 else '',
            ))
            for plugin_name in sorted(missing):
                print('  {name} (redirected to: {redirect})'.format(
                    name=plugin_name, redirect=our_redirects.get(plugin_name)))


def main():
    parser = argparse.ArgumentParser(description='meta/runtime.yml helper')

    subparsers = parser.add_subparsers(metavar='COMMAND')

    redirect_parser = subparsers.add_parser('redirect',
                                            help='Update redirections (meta/runtime.yml or symlinks)')
    redirect_parser.set_defaults(func=func_redirect)
    redirect_parser.add_argument('--target',
                                 required=True,
                                 metavar='[ meta | symlinks | both ]',
                                 help='Set to "meta", "symlinks", or "both"')
    redirect_parser.add_argument('--sort-plugin-routing',
                                 action='store_true',
                                 help='Sorts plugin routing data in meta/runtime.yml')
    redirect_parser.add_argument('--flatmap',
                                 action='store_true',
                                 help='Make sure that all redirections are there needed for flatmapping')

    check_ansible_base_redirects_parser = subparsers.add_parser('check-ansible-base-redirects',
                                                                help='Compare collection to redirects in '
                                                                     'ansible-base (needs to be installed)')
    check_ansible_base_redirects_parser.set_defaults(func=func_check_ansible_base_redirects)

    ansible_base_redirects_inventory_parser = subparsers.add_parser('ansible-base-redirects-inventory',
                                                                    help='List all collections that '
                                                                         'ansible-base (needs to be '
                                                                         'installed) redirects to in its '
                                                                         'ansible_builtin_runtime.yml')
    ansible_base_redirects_inventory_parser.set_defaults(func=func_ansible_base_redirects_inventory)

    validate_parser = subparsers.add_parser('validate',
                                            help='Makes sure plugins referenced for this collection '
                                                 'actually exist')
    validate_parser.set_defaults(func=func_validate)

    args = parser.parse_args()

    if getattr(args, 'func', None) is None:
        parser.print_help()
        return 2

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
