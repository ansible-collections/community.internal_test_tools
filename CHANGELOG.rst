======================================================
Community Internal Test Tools Collection Release Notes
======================================================

.. contents:: Topics


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

- open_url_test_lookup - Test plugin for the open_url test framework (DO NOT USE THIS!)

New Modules
-----------

- files_collect - Collect state of files and directories on disk
- files_diff - Check whether there were changes since files_collect was called

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

- community.internal_test_tools.fetch_url_test_module - Test module for fetch_url test framework
