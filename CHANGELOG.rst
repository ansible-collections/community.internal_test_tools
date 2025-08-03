======================================================
Community Internal Test Tools Collection Release Notes
======================================================

.. contents:: Topics

v0.18.0
=======

Release Summary
---------------

Major release with a removed feature.

Removed Features (previously deprecated)
----------------------------------------

- The deprecated extra sanity test runner has been removed. Consider using `antsibull-nox <https://ansible.readthedocs.io/projects/antsibull-nox/>`__ instead (https://github.com/ansible-collections/community.internal_test_tools/pull/156).

v0.17.1
=======

Release Summary
---------------

Bugfix release.

Bugfixes
--------

- Adjust ``ansible-collections.ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils.extract_warnings_texts()`` to breaking changes in ansible-core ``devel`` branch. Unfortunately `no stable API to query this information is available in ansible-core 2.19 <https://github.com/ansible/ansible/pull/85327#issuecomment-3050622410>`__ (https://github.com/ansible-collections/community.internal_test_tools/pull/151).

v0.17.0
=======

Release Summary
---------------

Maintenance release with deprecation of the extra sanity test runner.

Deprecated Features
-------------------

- The extra sanity test runner is deprecated. Consider using `antsibull-nox <https://ansible.readthedocs.io/projects/antsibull-nox/>`__ instead (https://github.com/ansible-collections/community.internal_test_tools/pull/150).

v0.16.0
=======

Release Summary
---------------

Feature and maintenance release with Data Tagging support.

Bugfixes
--------

- Support ansible-core's data tagging changes in ``ansible_collections.community.internal_test_tools.tests.unit.mock.loader.DictDataLoader`` (https://github.com/ansible-collections/community.internal_test_tools/pull/143).
- Support ansible-core's data tagging changes in ``ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils.set_module_args()`` (https://github.com/ansible-collections/community.internal_test_tools/pull/143).
- Support ansible-core's data tagging changes in ``ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils.trust`` (https://github.com/ansible-collections/community.internal_test_tools/pull/143).

v0.15.0
=======

Release Summary
---------------

Feature release preparing Data Tagging support.

Minor Changes
-------------

- Provide helper utility ``ansible_collections.community.internal_test_tools.tests.unit.utils.trust`` for tests that need to handle both ansible-core versions with and without Data Tagging:

  * The helper functions ``make_trusted()`` and ``make_untrusted()`` mark a value as trusted respectively untrusted (with Data Tagging), or as safe or unsafe (before Data Tagging).
  * The function ``is_trusted()`` allows to check with all versions of ansible-core whether a value is trusted (not unsafe) or not trusted (unsafe).
  * The constant ``SUPPORTS_DATA_TAGGING`` allows to decide whether ansible-core supports Data Tagging or not.

  Note that Data Tagging support right now is not implemented and will be added later (https://github.com/ansible-collections/community.internal_test_tools/pull/146)
- Provide helper utility function ``ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils.extract_warnings_texts()`` to extract warnings as strings from module results (https://github.com/ansible-collections/community.internal_test_tools/pull/147)

Breaking Changes / Porting Guide
--------------------------------

- The helper function ``ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils.set_module_args()`` is now a context manager. Please adapt uses accordingly (https://github.com/ansible-collections/community.internal_test_tools/pull/144).

v0.14.0
=======

Release Summary
---------------

Feature release.

Minor Changes
-------------

- fetch_url and open_url unit test frameworks - add helper methods ``result_error_json()`` to set JSON bodies for error results (https://github.com/ansible-collections/community.internal_test_tools/pull/140).

v0.13.0
=======

Release Summary
---------------

Feature release.

Minor Changes
-------------

- extra sanity tests runner - add ``--break-system-packages`` to ``pip`` invocations (https://github.com/ansible-collections/community.internal_test_tools/pull/137).
- extra sanity tests runner - bump default Python version used for tests to 3.13 (https://github.com/ansible-collections/community.internal_test_tools/pull/137).
- extra sanity tests runner - update fallback image name and use Python 3.13 inside the container (https://github.com/ansible-collections/community.internal_test_tools/pull/137).

v0.12.0
=======

Release Summary
---------------

Feature release.

Minor Changes
-------------

- fetch_url and open_url unit test frameworks - use the ``tests.unit.compat.mock`` module everywhere so that ``unittest.mock`` is used instead of ``mock`` on Python 3 (https://github.com/ansible-collections/community.internal_test_tools/pull/130).
- open_url and fetch_url unit test frameworks - allow to check for form value arrays (https://github.com/ansible-collections/community.internal_test_tools/pull/125).

Removed Features (previously deprecated)
----------------------------------------

- Removed the ``ansible_builtin_runtime`` tool (https://github.com/ansible-collections/community.internal_test_tools/issues/111, https://github.com/ansible-collections/community.internal_test_tools/pull/131).

v0.11.0
=======

Release Summary
---------------

Feature, bugfix, and maintenance release.

Minor Changes
-------------

- extra sanity test runner - make sure that a ``ansible_collections`` ancestor directory is also copied into the Docker container (https://github.com/ansible-collections/community.internal_test_tools/pull/103).

Breaking Changes / Porting Guide
--------------------------------

- The internal test module ``fetch_url_test_module`` has been renamed to ``_fetch_url_test_module``, and the internal test lookup plugin ``open_url_test_lookup`` has been renamed to ``_open_url_test_lookup``. This emphasizes that these plugins are private and not supposed to be used by end-users  (https://github.com/ansible-collections/community.internal_test_tools/pull/112).

Deprecated Features
-------------------

- The ``tools/ansible_builtin_runtime.py`` tool is deprecated and will be removed in a future version. If anyone is interested in keeping this tool, please comment on the `tool removal issue <https://github.com/ansible-collections/community.internal_test_tools/issues/111>`__ (https://github.com/ansible-collections/community.internal_test_tools/issues/111).

Bugfixes
--------

- extra sanity test runner - run pip via Python instead of running it directly; also set ``PIP_BREAK_SYSTEM_PACKAGES=1`` in the environment (https://github.com/ansible-collections/community.internal_test_tools/pull/104).

v0.10.1
=======

Release Summary
---------------

Maintenance release to test whether publishing community collections works.

v0.10.0
=======

Release Summary
---------------

Maintenance release with updated documentation and removal of a deprecated tool.

From this version on, community.internal_test_tools is using the new `Ansible semantic markup
<https://docs.ansible.com/ansible/devel/dev_guide/developing_modules_documenting.html#semantic-markup-within-module-documentation>`__
in its documentation. If you look at documentation with the ansible-doc CLI tool
from ansible-core before 2.15, please note that it does not render the markup
correctly. You should be still able to read it in most cases, but you need
ansible-core 2.15 or later to see it as it is intended. Alternatively you can
look at `the docsite <https://ansible-collections.github.io/community.internal_test_tools/branch/main/>`__
for the rendered HTML version of the documentation of the latest release.

Removed Features (previously deprecated)
----------------------------------------

- Removed the deprecated ``meta/runtime.yml`` tool (https://github.com/ansible-collections/community.internal_test_tools/issues/79, https://github.com/ansible-collections/community.internal_test_tools/pull/91).

Known Issues
------------

- Ansible markup will show up in raw form on ansible-doc text output for ansible-core before 2.15. If you have trouble deciphering the documentation markup, please upgrade to ansible-core 2.15 (or newer), or read the HTML documentation on https://ansible-collections.github.io/community.internal_test_tools/branch/main/.

v0.9.0
======

Release Summary
---------------

Feature release with improved extra sanity test runner.

Minor Changes
-------------

- Let the extra sanity test runner report bad test descriptors as errors (https://github.com/ansible-collections/community.internal_test_tools/pull/89).
- Use Python 3.10 instead of Python 3.8 for the extra sanity test runner (https://github.com/ansible-collections/community.internal_test_tools/pull/88).

Deprecated Features
-------------------

- The meta/runtime.yml helper tool ``tools/meta_runtime.py`` is deprecated and will be removed soon. If you need it, please comment on the issue and/or stick to a version of community.internal_test_tools that is known to still includes it (https://github.com/ansible-collections/community.internal_test_tools/issues/79, https://github.com/ansible-collections/community.internal_test_tools/pull/90).

v0.8.0
======

Release Summary
---------------

Maintenance release with updated documentation and licensing information.

Minor Changes
-------------

- The collection repository conforms to the `REUSE specification <https://reuse.software/spec/>`__ except for the changelog fragments (https://github.com/ansible-collections/community.internal_test_tools/pull/75).

v0.7.0
======

Release Summary
---------------

Regular feature release.

Minor Changes
-------------

- All software licenses are now in the ``LICENSES/`` directory of the collection root. Moreover, ``SPDX-License-Identifier:`` is used to declare the applicable license for every file that is not automatically generated (https://github.com/ansible-collections/community.internal_test_tools/pull/69).
- open_url and fetch_url unit test frameworks - allow to check for ``timeout``, ``url_username``, ``url_password``, and ``force_basic_auth`` settings (https://github.com/ansible-collections/community.internal_test_tools/pull/65).

v0.6.1
======

Release Summary
---------------

Regular bugfix release.

Bugfixes
--------

- extra sanity test runner - bump default Docker image fallback to container currently used by ansible-test in devel branch (https://github.com/ansible-collections/community.internal_test_tools/pull/55).
- extra sanity test runner - fix default Docker image detection to work with ansible-test from ansible-core 2.12.2 on (https://github.com/ansible-collections/community.internal_test_tools/pull/55).

v0.6.0
======

Release Summary
---------------

Feature and bugfix release.

Minor Changes
-------------

- fetch_url test framework - make behavior more similar to latest ansible-core ``devel`` branch, and include ``closed`` property for response objects (https://github.com/ansible-collections/community.internal_test_tools/pull/52).
- open_url test framework - include ``closed`` property for response objects (https://github.com/ansible-collections/community.internal_test_tools/pull/52).

Bugfixes
--------

- fetch_url_test_module - fix usage of ``fetch_url`` with changes in latest ansible-core ``devel`` branch (https://github.com/ansible-collections/community.internal_test_tools/pull/52).
- files_collect, files_diff - ignore ``atime`` since that does not indicate that a file was modified (https://github.com/ansible-collections/community.internal_test_tools/pull/54).

v0.5.0
======

Release Summary
---------------

Feature release with various tool improvements.

Minor Changes
-------------

- ``fetch_url`` and ``open_url`` test frameworks - output number of expected and actual calls when number of actual calls is too low.
- ansible_builtin_runtime tool - allow to specify collection root directory for ``check-ansible-core-redirects`` subcommand (https://github.com/ansible-collections/community.internal_test_tools/pull/51).
- ansible_builtin_runtime tool - make tool executable (https://github.com/ansible-collections/community.internal_test_tools/pull/51).
- extra sanity test runner - add options ``--bot`` and ``--junit`` to create results that ansibullbot and AZP can parse (https://github.com/ansible-collections/community.internal_test_tools/pull/41).
- extra sanity test runner - bump default Python version from 3.7 to 3.8 (https://github.com/ansible-collections/community.internal_test_tools/pull/49).
- meta_runtime tool - allow to specify collection root directory for all subcommands (https://github.com/ansible-collections/community.internal_test_tools/pull/51).

Breaking Changes / Porting Guide
--------------------------------

- ansible_builtin_runtime tool - renamed ``check-ansible-base-redirects`` subcommand to ``check-ansible-core-redirects`` (https://github.com/ansible-collections/community.internal_test_tools/pull/51).

Bugfixes
--------

- ansible_builtin_runtime tool - fix subcommand ``check-ansible-core-redirects`` (https://github.com/ansible-collections/community.internal_test_tools/pull/51).
- extra sanity test runner - bump default Docker image fallback to container currently used by ansible-test in devel branch (https://github.com/ansible-collections/community.internal_test_tools/pull/50).
- extra sanity test runner - fix default Docker image detection to work with ansible-test from ansible-core 2.12 (https://github.com/ansible-collections/community.internal_test_tools/pull/47).

v0.4.0
======

Release Summary
---------------

Add bugfixes for and new features to the ``open_url``/``fetch_url`` test framework.

Minor Changes
-------------

- fetch_url and open_url testing frameworks - allow to check query parameters of URLs (https://github.com/ansible-collections/community.internal_test_tools/pull/33).
- fetch_url and open_url testing frameworks - allow to compare URLs without query and/or fragment (https://github.com/ansible-collections/community.internal_test_tools/pull/33).
- fetch_url and open_url testing frameworks - allow to parse and check JSON data (https://github.com/ansible-collections/community.internal_test_tools/pull/34).

Bugfixes
--------

- fetch_url testing framework - return ``url`` as part of ``info`` (https://github.com/ansible-collections/community.internal_test_tools/pull/33).

v0.3.0
======

Minor Changes
-------------

- Added a framework for testing plugins using ``open_url`` from ``ansible.module_utils.urls`` (https://github.com/ansible-collections/community.internal_test_tools/pull/24).
- The ``fetch_url`` testing framework now allows to match the provided content (https://github.com/ansible-collections/community.internal_test_tools/pull/31).
- There are now a `meta/runtime.yml and ansible_builtin_runtime.yml helper tools <https://github.com/ansible-collections/community.internal_test_tools/tree/main/tools/README.md>`_ which allows to convert between symlinks and redirects in ``meta/runtime.yml``, allows to compare ansible-base's ``lib/ansible/config/ansible_builtin_runtime.yml`` with this collection, and verify that plugins mentioned actually exist.

Bugfixes
--------

- Fix form value present test for ``fetch_url`` testing framework (https://github.com/ansible-collections/community.internal_test_tools/pull/24).
- Fix header test for ``fetch_url`` testing framework (https://github.com/ansible-collections/community.internal_test_tools/pull/24).

New Plugins
-----------

Lookup
~~~~~~

- community.internal_test_tools.open_url_test_lookup - Test plugin for the open_url test framework (DO NOT USE THIS!)

New Modules
-----------

- community.internal_test_tools.files_collect - Collect state of files and directories on disk
- community.internal_test_tools.files_diff - Check whether there were changes since files_collect was called

v0.2.1
======

Release Summary
---------------

Re-release because Galaxy did not accept a tag with spaces in ``galaxy.yml``. No other changes besides that the changelog moved to the root directory.

v0.2.0
======

Major Changes
-------------

- There is now a `extra sanity test runner <https://github.com/ansible-collections/community.internal_test_tools/tree/main/tools/README.md>`_ which allows to easily run extra sanity tests. This is a stop-gap solution until ansible-test supports sanity test plugins.

v0.1.1
======

Release Summary
---------------

Initial release.

New Modules
-----------

- community.internal_test_tools.community.internal_test_tools.fetch_url_test_module - Test module for fetch_url test framework
