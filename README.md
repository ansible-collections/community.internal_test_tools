# Internal Test Tools Collection
[![CI](https://github.com/ansible-collections/community.internal_test_tools/workflows/CI/badge.svg?event=push)](https://github.com/ansible-collections/community.internal_test_tools/actions)
[![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/community.internal_test_tools)](https://codecov.io/gh/ansible-collections/community.internal_test_tools)

This collection provides useful test tools for other collections. It is **NOT** aimed at Ansible users, but at collection developers!

## Tested with Ansible

Ansible 2.9 and Ansible `devel` branch.

## Included content

- [`tests/unit/compat/` package](https://github.com/ansible-collections/community.internal_test_tools/tree/main/tests/unit/compat/)
- [`tests/unit/mock/` package](https://github.com/ansible-collections/community.internal_test_tools/tree/main/tests/unit/mock/)
- [`tests/unit/plugins/modules/utils.py`](https://github.com/ansible-collections/community.internal_test_tools/tree/main/tests/unit/plugins/modules/utils.py/)
- [`tests/unit/utils/fetch_url_module_framework.py`](https://github.com/ansible-collections/community.internal_test_tools/tree/main/tests/unit/utils/fetch_url_module_framework.py)
- [`tests/unit/utils/open_url_framework.py`](https://github.com/ansible-collections/community.internal_test_tools/tree/main/tests/unit/utils/open_url_framework.py)
- [extra sanity test runner](https://github.com/ansible-collections/community.internal_test_tools/tree/main/tools/README.md)
- [meta/runtime.yml helper](https://github.com/ansible-collections/community.internal_test_tools/tree/main/tools/README.md)

## Contributing to this collection

Please follow the general Ansible contributor guidelines; see the [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html).

## Release notes

A changelog can be found [in the GitHub repository](https://github.com/ansible-collections/community.internal_test_tools/tree/main/CHANGELOG.rst).

## More information

- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Developing Collections section in the Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## Licensing

GNU General Public License v3.0 or later.

See [COPYING](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
