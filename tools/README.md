# Tools

## Extra sanity test runner

This is a small tool to run sanity tests similar to the [ansible-base-specific code-smell tests](https://github.com/ansible/ansible/tree/devel/test/sanity/code-smell) and the [code-smell tests integrated into `ansible-test sanity`](https://github.com/ansible/ansible/tree/devel/test/lib/ansible_test/_data/sanity/code-smell).

It does not have useful features such as change detection, but it can be restricted to certain targets. The hope is that eventually, ansible-test will have a plugin infrastructure which allows it to run such tests itself.

The runner can, for example, be used to lint changelog fragments, to check for unwanted files, or to check for new versions of bundled scripts.

Note that tests are **always** run in a docker container (using ansible-test's `default` container). There's currently no way to disable that. Also note that as opposed to ansible-test, the runner does not even try to ensure that the files copied into the container are usable as an Ansible collection.

An advantage over ansible-test's code-smell plugins is that Python dependencies and a preferred Python version for running the tests can be specified per test.

Once ansible-test supports custom code-smell plugins, this tool will be deprecated in favor of ansible-test.

### Syntax

The runner looks for tests in `tests/sanity/extra/`. Every test must consist of a JSON config file `<test>.json` and a Python script `<test>.py`. The executable does not need to be executable. It will be invoked as `python<version> tests/sanity/extra/<test>.py <target>...`, where `<target>...` is a list of files that the test is supposed to check. This list will be compiled according to the configuration file.

Besides very similar target selection configurations to ansible-test, it allows to specify `"python": "<version>"` for the Python version to use, and `"requirements": [...]` to install additional Python requirements needed for this test.

### Example usage: lint changelog fragments

This example runs [`ansibulled-changelog lint`](https://github.com/ansible-community/ansibulled) to lint all changelog fragments. The wrapper script uses Python 3.7, and installs [ansibulled](https://github.com/ansible-community/ansibulled) before running.

`tests/sanity/extra/changelog.json`:
```.json
{
    "python": "3.7",
    "output": "path-line-column-message",
    "prefixes": [
        "changelogs/fragments/"
    ],
    "requirements": [
        "git+git://github.com/ansible-community/ansibulled.git@pip-installable#egg=ansibulled"
    ]
}
```

`tests/sanity/extra/changelog.py`:
```.py
#!/usr/bin/env python
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import os
import sys
import subprocess


def main():
    paths = sys.argv[1:] or sys.stdin.read().splitlines()

    allowed_extensions = ('.yml', '.yaml')

    for path in paths:
        ext = os.path.splitext(path)[1]

        if ext not in allowed_extensions:
            print('%s:%d:%d: extension must be one of: %s' % (path, 0, 0, ', '.join(allowed_extensions)))

    cmd = ['ansibulled-changelog', 'lint'] + paths
    subprocess.check_call(cmd)


if __name__ == '__main__':
    main()
```
