<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# Internal Test Tools Collection
[![Documentation](https://img.shields.io/badge/docs-brightgreen.svg)](https://ansible-collections.github.io/community.internal_test_tools/branch/main/)
[![CI](https://github.com/ansible-collections/community.internal_test_tools/actions/workflows/nox.yml/badge.svg?branch=main)](https://github.com/ansible-collections/community.internal_test_tools/actions)
[![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/community.internal_test_tools)](https://codecov.io/gh/ansible-collections/community.internal_test_tools)
[![REUSE status](https://api.reuse.software/badge/github.com/ansible-collections/community.internal_test_tools)](https://api.reuse.software/info/github.com/ansible-collections/community.internal_test_tools)

This collection provides useful test tools for other collections. It is **NOT** aimed at Ansible users, but at collection developers!

Please note that this collection does **not** support Windows targets.

## Code of Conduct

We follow [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html) in all our interactions within this project.

If you encounter abusive behavior violating the [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html), please refer to the [policy violations](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html#policy-violations) section of the Code of Conduct for information on how to raise a complaint.

## Communication

* Join the Ansible forum:
  * [Tag `internal-test-tools`](https://forum.ansible.com/tag/internal-test-tools): discuss the collection and the test tools it provides.
  * [Collection Development](https://forum.ansible.com/c/project/collection-development/27): discuss development and testing of collections. Please add the `internal-test-tools` tag when starting new discussions involving this collection.
  * [Social Spaces](https://forum.ansible.com/c/chat/4): gather and interact with fellow enthusiasts.
  * [News & Announcements](https://forum.ansible.com/c/news/5): track project-wide announcements including social events.

* The Ansible [Bullhorn newsletter](https://docs.ansible.com/ansible/devel/community/communication.html#the-bullhorn): used to announce releases and important changes.

For more information about communication, see the [Ansible communication guide](https://docs.ansible.com/ansible/devel/community/communication.html).

## Tested with Ansible

Tested with the current Ansible 2.9, ansible-base 2.10, ansible-core 2.11, ansible-core 2.12, ansible-core 2.13, ansible-core 2.14, ansible-core 2.15, ansible-core 2.16, ansible-core 2.17, and ansible-core 2.18 releases and the current development version of ansible-core. Ansible versions before 2.9.10 are not supported.

## Collection Documentation

We publish [**latest commit** collection documentation](https://ansible-collections.github.io/community.internal_test_tools/branch/main/) which shows docs for the _latest commit in the `main` branch_.

## Included content

- [`tests/unit/compat/` package](https://github.com/ansible-collections/community.internal_test_tools/tree/main/tests/unit/compat/)
- [`tests/unit/mock/` package](https://github.com/ansible-collections/community.internal_test_tools/tree/main/tests/unit/mock/)
- [`tests/unit/plugins/modules/utils.py`](https://github.com/ansible-collections/community.internal_test_tools/tree/main/tests/unit/plugins/modules/utils.py/)
- [`tests/unit/utils/fetch_url_module_framework.py`](https://github.com/ansible-collections/community.internal_test_tools/tree/main/tests/unit/utils/fetch_url_module_framework.py)
- [`tests/unit/utils/open_url_framework.py`](https://github.com/ansible-collections/community.internal_test_tools/tree/main/tests/unit/utils/open_url_framework.py)
- [extra sanity test runner](https://github.com/ansible-collections/community.internal_test_tools/tree/main/tools/README.md)

## Contributing to this collection

Please create issues to report problems or request new features, and create PRs to fix bugs or add new features. If you want to do a refactoring PR, please create an issue first to discuss the refactoring.

Please follow the general Ansible contributor guidelines; see the [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html).

## Release notes

A changelog can be found [in the GitHub repository](https://github.com/ansible-collections/community.internal_test_tools/tree/main/CHANGELOG.md).

## Releasing, Deprecation and Versioning

We release new versions once there are new features or bugfixes. Deprecations can happen, and we try to announce them a long time in advance. We currently do not plan breaking changes, so there will be no new major release anytime soon, except maybe a version 1.0.0.

## More information

- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Developing Collections section in the Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## Licensing

This collection is primarily licensed and distributed as a whole under the GNU General Public License v3.0 or later.

See [LICENSES/GPL-3.0-or-later.txt](https://github.com/ansible-collections/community.internal_test_tools/blob/main/COPYING) for the full text.

All files have a machine readable `SDPX-License-Identifier:` comment denoting its respective license(s) or an equivalent entry in an accompanying `.license` file. Only changelog fragments (which will not be part of a release) are covered by a blanket statement in `.reuse/dep5`. This conforms to the [REUSE specification](https://reuse.software/spec/).
