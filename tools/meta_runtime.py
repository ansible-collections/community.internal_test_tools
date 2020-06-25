#!/usr/bin/env python

# Copyright: (c) 2020, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import collections
import argparse
import os
import sys

import yaml

try:
    # use C version if possible for speedup
    from yaml import CSafeLoader as _SafeLoader
    from yaml import CSafeDumper as _SafeDumper
except ImportError:
    from yaml import SafeLoader as _SafeLoader
    from yaml import SafeDumper as _SafeDumper


def load_yaml(path):
    """
    Load and parse YAML file ``path``.
    """
    with open(path, 'r') as stream:
        return yaml.load(stream, Loader=_SafeLoader)


def store_yaml(path, content):
    """
    Store ``content`` as YAML file under ``path``.
    """
    with open(path, 'w') as stream:
        dumper = _SafeDumper
        dumper.ignore_aliases = lambda *args: True
        yaml.dump(content, stream, default_flow_style=False, encoding='utf-8', sort_keys=False, Dumper=dumper)


PLUGIN_TYPES = [
    'doc_fragments',
    'action',
    'cache',
    'callback',
    'connection',
    'shell',
    'modules',
    'module_utils',
    'lookup',
    'filter',
    'test',
    'strategy',
    'terminal',
    'vars',
    'cliconf',
    'netconf',
    'inventory',
    'httpapi',
    'become',
]


def record_redirect(plugin_type, record, source, destination):
    if source in record:
        if record[source] != destination:
            raise Exception('ERROR: {plugin_type} {source} maps to '
                            'both {destination_1} and {destination_2}'.format(
                plugin_type=plugin_type,
                source=source,
                destination_1=record[source],
                destination_2=destination,
            ))
    record[source] = destination


def path_to_name(path, base_dir):
    path = path[:-len('.py')]
    redirect_name = os.path.normpath(os.path.relpath(path, base_dir)).replace(os.path.sep, '.')
    return redirect_name


def scan_file_redirects(redirects, remove=False):
    for plugin_type in PLUGIN_TYPES:
        plugin_redirects = redirects[plugin_type]
        base_dir = os.path.join('plugins', plugin_type)
        for root, dirnames, filenames in os.walk(base_dir):
            for filename in filenames:
                if not filename.endswith('.py'):
                    continue
                if filename in ('__init__', ):
                    continue
                path = os.path.join(root, filename)
                if os.path.islink(path):
                    dest = os.readlink(path)
                    if not dest.endswith('.py'):
                        print('WARNING: link {link} does not point to Python file, '
                              'but to {dest}'.format(link=path, dest=dest))
                        continue
                    dest_path = os.path.join(root, dest)
                    source = path_to_name(path, base_dir)
                    destination = path_to_name(dest_path, base_dir)
                    record_redirect(plugin_type, plugin_redirects, source, destination)
                    if remove:
                        os.unlink(path)


def scan_flatmap_redirects(redirects):
    plugin_type = 'modules'
    plugin_redirects = redirects[plugin_type]
    base_dir = os.path.join('plugins', plugin_type)
    for root, dirnames, filenames in os.walk(base_dir):
        if root == base_dir:
            continue
        for filename in filenames:
            if not filename.endswith('.py'):
                continue
            if filename in ('__init__', ):
                continue
            source = path_to_name(os.path.join(base_dir, filename), base_dir)
            destination = path_to_name(os.path.join(root, filename), base_dir)
            record_redirect(plugin_type, plugin_redirects, source, destination)


def name_to_path(name, base_dir):
    return os.path.join(base_dir, name.replace('.', os.path.sep) + '.py')


def add_file_redirects(redirects):
    for plugin_type in PLUGIN_TYPES:
        base_dir = os.path.join('plugins', plugin_type)
        for source, destination in redirects[plugin_type].items():
            src = name_to_path(source, base_dir)
            dst = name_to_path(destination, base_dir)
            rel_dst = os.path.normpath(os.path.relpath(dst, os.path.dirname(src)))
            if os.path.islink(src):
                if os.path.normpath(os.readlink(src)) == rel_dst:
                    continue
            os.symlink(rel_dst, src)


def extract_meta_redirects(redirects, runtime, collection_name, remove=False):
    plugin_routing = runtime.get('plugin_routing') or {}
    collection_prefix = '{name}.'.format(name=collection_name)
    for plugin_type in PLUGIN_TYPES:
        plugins = plugin_routing.get(plugin_type)
        plugin_redirects = redirects[plugin_type]
        if plugins:
            for plugin_name, plugin_data in plugins.items():
                redirect = plugin_data.get('redirect')
                if redirect and redirect.startswith(collection_prefix):
                    record_redirect(
                        plugin_type, plugin_redirects, plugin_name,
                        redirect[len(collection_prefix):])
                    if remove:
                        del plugin_data['redirect']


def add_meta_redirects(redirects, runtime, collection_name):
    plugin_routing = runtime.get('plugin_routing')
    collection_prefix = '{name}.'.format(name=collection_name)
    for plugin_type in PLUGIN_TYPES:
        for source, destination in redirects[plugin_type].items():
            if plugin_routing is None:
                runtime['plugin_routing'] = plugin_routing = dict()
            if plugin_type not in plugin_routing:
                plugin_routing[plugin_type] = dict()
            if source not in plugin_routing[plugin_type]:
                plugin_routing[plugin_type][source] = dict()
            plugin_routing[plugin_type][source]['redirect'] = (
                '{collection_name}.{destination}'.format(
                    collection_name=collection_name,
                    destination=destination,
                )
            )


def sort_plugin_routing(runtime):
    plugin_routing = runtime.get('plugin_routing')
    if not plugin_routing:
        return
    for plugin_type in PLUGIN_TYPES:
        plugins = plugin_routing.get(plugin_type)
        if not plugins:
            continue
        plugin_routing[plugin_type] = dict([
            (key, value) for key, value in sorted(plugins.items())
        ])


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

    runtime_path = 'meta/runtime.yml'

    # Load basic information on collection
    galaxy = load_yaml('galaxy.yml')
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

    scan_file_redirects(redirects)
    extract_meta_redirects(redirects, runtime, collection_name)

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
    store_yaml(runtime_path, runtime)

    if symlink_redirects:
        add_file_redirects(redirects)
    else:
        scan_file_redirects(redirects, remove=True)


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

    args = parser.parse_args()

    if getattr(args, 'func', None) is None:
        parser.print_help()
        return 2

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
