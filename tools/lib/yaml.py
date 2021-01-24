# Copyright: (c) 2020, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

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
