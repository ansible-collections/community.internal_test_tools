#!/usr/bin/env python

# Copyright: (c) 2020, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


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


GALAXY_PATH = 'galaxy.yml'
RUNTIME_PATH = 'meta/runtime.yml'

REQUIRE_INIT_PY = False


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
            raise Exception(
                'ERROR: {plugin_type} {source} maps to '
                'both {destination_1} and {destination_2}'.format(
                    plugin_type=plugin_type,
                    source=source,
                    destination_1=record[source],
                    destination_2=destination,
                ))
    record[source] = destination


def path_to_name(path, base_dir, remove_extension=True):
    if remove_extension:
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


def scan_plugins(plugins, redirects, runtime, all_plugins=False):
    plugin_routing = runtime.get('plugin_routing') or {}
    for plugin_type in PLUGIN_TYPES:
        plugins_set = plugins[plugin_type]
        plugin_redirects = redirects[plugin_type]
        for source, destination in plugin_redirects.items():
            plugins_set.add(source)
            plugins_set.add(destination)
        base_dir = os.path.join('plugins', plugin_type)
        for root, dirnames, filenames in os.walk(base_dir):
            if plugin_type == 'module_utils':
                for dirname in dirnames:
                    path = os.path.join(root, dirname)
                    if REQUIRE_INIT_PY:
                        init_path = os.path.join(path, '__init__.py')
                        if os.path.isfile(init_path):
                            plugins_set.add(path_to_name(path, base_dir, remove_extension=False))
                    else:
                        plugins_set.add(path_to_name(path, base_dir, remove_extension=False))
            for filename in filenames:
                if not filename.endswith('.py'):
                    continue
                if filename in ('__init__', ):
                    continue
                path = os.path.join(root, filename)
                plugins_set.add(path_to_name(path, base_dir))
        if plugin_type in plugin_routing:
            for plugin_name, plugin_data in plugin_routing[plugin_type].items():
                if 'tombstone' in plugin_data or all_plugins:
                    plugins_set.add(plugin_name)


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
