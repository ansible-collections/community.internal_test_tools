#!/usr/bin/env python

# Copyright (c) 2020, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import argparse
import os
import sys

# Make sure that our collection root is in the Python package search path.
# This makes it possible to import `tools.lib.xxx` no matter whether this
# script was invoked by `python -m tools.xxx` or by `tools/xxx.py`.
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tools.lib.ansible import PLUGIN_TYPES
from tools.lib.meta_runtime import (
    add_file_redirects,
    add_meta_redirects,
    extract_meta_redirects,
    scan_file_redirects,
    scan_flatmap_redirects,
    scan_plugins,
    sort_plugin_routing,
)
from tools.lib.yaml import load_yaml, store_yaml


GALAXY_PATH = 'galaxy.yml'
RUNTIME_PATH = 'meta/runtime.yml'


def func_redirect(args):
    collection_root = args.collection_root
    galaxy_path = os.path.join(collection_root, GALAXY_PATH)
    runtime_path = os.path.join(collection_root, RUNTIME_PATH)

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
    galaxy = load_yaml(galaxy_path)
    collection_name = '{namespace}.{name}'.format(**galaxy)
    print('Working on collection {name}'.format(name=collection_name))

    # Load meta/runtime
    if os.path.exists(runtime_path):
        runtime = load_yaml(runtime_path)
    else:
        runtime = None

    if not runtime:
        runtime = dict()

    # Scan for wanted set of redirects
    redirects = dict()
    for plugin_type in PLUGIN_TYPES:
        redirects[plugin_type] = dict()

    scan_file_redirects(redirects, collection_root=collection_root)
    extract_meta_redirects(redirects, runtime, collection_name)

    # Scan flatmap redirects
    if args.flatmap:
        scan_flatmap_redirects(redirects, collection_root=collection_root)

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
    store_yaml(runtime_path, runtime)

    if symlink_redirects:
        add_file_redirects(redirects, collection_root=collection_root)
    else:
        scan_file_redirects(redirects, remove=True, collection_root=collection_root)


def func_validate(args):
    collection_root = args.collection_root
    galaxy_path = os.path.join(collection_root, GALAXY_PATH)
    runtime_path = os.path.join(collection_root, RUNTIME_PATH)

    # Load basic information on collection
    galaxy = load_yaml(galaxy_path)
    collection_name = '{namespace}.{name}'.format(**galaxy)
    print('Working on collection {name}'.format(name=collection_name))

    # Load meta/runtime
    if os.path.exists(runtime_path):
        runtime = load_yaml(runtime_path)
    else:
        runtime = None

    if not runtime:
        runtime = dict()

    # Collect all redirects and plugins
    redirects = dict()
    empty_redirects = dict()
    plugins = dict()
    for plugin_type in PLUGIN_TYPES:
        redirects[plugin_type] = dict()
        empty_redirects[plugin_type] = dict()
        plugins[plugin_type] = set()

    scan_file_redirects(redirects, collection_root=collection_root)
    extract_meta_redirects(redirects, runtime, collection_name)

    scan_plugins(plugins, empty_redirects, runtime, collection_root=collection_root, all_plugins=True)

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

    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument('--collection-root', default='.',
                             help='The root directory of the collection to work on')

    subparsers = parser.add_subparsers(metavar='COMMAND')

    redirect_parser = subparsers.add_parser('redirect',
                                            parents=[base_parser],
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

    validate_parser = subparsers.add_parser('validate',
                                            parents=[base_parser],
                                            help='Makes sure plugins referenced for this collection '
                                                 'actually exist')
    validate_parser.set_defaults(func=func_validate)

    args = parser.parse_args()

    if getattr(args, 'func', None) is None:
        parser.print_help()
        return 2

    collection_root = args.collection_root
    if not os.path.exists(os.path.join(collection_root, GALAXY_PATH)):
        raise Exception("This tool must be run in a collection's root directory, that contains galaxy.yml.")

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
