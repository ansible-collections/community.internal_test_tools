..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.internal_test_tools.docsite.files_diff:

Checking for file modifications with ``files_collect`` and ``files_diff``
=========================================================================

The :anscollection:`community.internal_test_tools collection <community.internal_test_tools#collection>` offers two modules:

* :ansplugin:`community.internal_test_tools.files_collect#module`: collect state of files or directories;
* :ansplugin:`community.internal_test_tools.files_diff#module`: check these files or directories for changes.

These allow to check that modules actually do not modify a file, or only modify specific files. The :ansplugin:`community.internal_test_tools.files_diff#module` module returns details on which files and directories have been added, removed, changed. It also returns the content of the changed files so you do not need to add a :ansplugin:`ansible.builtin.fetch#module` task to read the changed files to check their content.

.. versionadded:: 0.3.0

Example for test that should not modify a file
----------------------------------------------

In the :ansplugin:`community.crypto.openssl_privatekey_convert#module` integration tests, we want to make sure that
the module does not only return :ansretval:`changed=false`, but also does not touch the file it operates on:

.. code-block:: yaml+jinja

    - name: Collect file information
      community.internal_test_tools.files_collect:
        files:
          - path: '{{ remote_tmp_dir }}/output_1.pem'
      register: convert_file_info_data

    - name: Convert (idempotent)
      community.crypto.openssl_privatekey_convert:
        src_path: '{{ remote_tmp_dir }}/privatekey_rsa_pass1.pem'
        src_passphrase: secret
        dest_path: '{{ remote_tmp_dir }}/output_1.pem'
        dest_passphrase: hunter2
        format: pkcs8
      register: convert_idem

    - name: Check whether file changed
      community.internal_test_tools.files_diff:
        state: '{{ convert_file_info_data }}'
      register: convert_file_info

    - name: Verify that nothing changed
      assert:
        that:
          # Check the module's result
          - convert_idem is not changed
          # Verify that the file was not changed
          - convert_file_info is not changed
