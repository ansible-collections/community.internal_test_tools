======================================================
Community Internal Test Tools Collection Release Notes
======================================================

.. contents:: Topics


v0.2.1
======

Release Summary
---------------

Re-release because Galaxy did not accept a tag with spaces in ``galaxy.yml``. No other changes.

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
