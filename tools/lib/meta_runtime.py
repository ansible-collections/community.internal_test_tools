# Copyright (c) 2020, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os

from .ansible import PLUGIN_TYPES
from .yaml import load_yaml


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


def scan_file_redirects(redirects, collection_root='.', remove=False):
    for plugin_type in PLUGIN_TYPES:
        if plugin_type in ('test', 'filter'):
            # Test and filter plugins are not coupled to filenames
            continue
        plugin_redirects = redirects[plugin_type]
        base_dir = os.path.join(collection_root, 'plugins', plugin_type)
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


def scan_plugins(plugins, redirects, runtime, collection_root='.', all_plugins=False):
    plugin_routing = runtime.get('plugin_routing') or {}
    for plugin_type in PLUGIN_TYPES:
        plugins_set = plugins[plugin_type]
        plugin_redirects = redirects[plugin_type]
        for source, destination in plugin_redirects.items():
            plugins_set.add(source)
            plugins_set.add(destination)
        base_dir = os.path.join(collection_root, 'plugins', plugin_type)
        for root, dirnames, filenames in os.walk(base_dir):
            if plugin_type == 'module_utils':
                for dirname in dirnames:
                    path = os.path.join(root, dirname)
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
                    if remove and plugin_type not in ('test', 'filter'):
                        del plugin_data['redirect']


def load_ansible_core_runtime():
    # Load ansible-core's ansible.builtin runtime
    from ansible import release as ansible_release

    ansible_builtin_runtime_path = os.path.join(
        os.path.dirname(ansible_release.__file__), 'config', 'ansible_builtin_runtime.yml')

    return load_yaml(ansible_builtin_runtime_path)
