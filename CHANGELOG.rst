=================================================
Branic System Management Collection Release Notes
=================================================

.. contents:: Topics

v1.2.0
======

Release Summary
---------------

Extends install_cloud_clis with OCM and Google Workspace CLIs, hardens ROSA
installs against mirror lag, and isolates per-CLI failures.

Minor Changes
-------------

- install_cloud_clis role - add Google Workspace CLI (gws) installation from GitHub releases
- install_cloud_clis role - add OCM CLI (openshift-online/ocm-cli) installation support with bash completion
- install_cloud_clis role - isolate each CLI install in block/rescue so one component failure does not block remaining installs
- install_cloud_clis role - loop CLI installs from install_cloud_clis_cli_installers to reduce duplicated task definitions in main.yml

Bugfixes
--------

- install_cloud_clis role - resolve ROSA CLI install version from mirror.openshift.com availability so a GitHub release ahead of the mirror does not fail the play

v1.1.0
======

Release Summary
---------------

Feature release adding systemd unit management, sysctl configuration, and package replacement capabilities.

Minor Changes
-------------

- Add ``ansible.posix`` collection dependency.
- Normalize role ``meta/main.yml``; ``version_added: 1.0.0`` on argument specs.
- openshift_local - add optional ``openshift_local_crc_version`` to pin a CRC release (validated before download).
- system_config and user_config roles can manage systemd units (system and user scope).
- system_config role — add ``system_config_package_replacements`` for ``dnf swap`` pairs (optional ``allowerasing``), running after repo setup and before DNF package install.
- system_config role — add sysctl configuration support.

v1.0.0
======

Release Summary
---------------

Initial release of the collection

Minor Changes
-------------

- Add ``openshift_local`` role to install or upgrade OpenShift Local (CRC) with optional host checks, configurable ``crc`` settings, and ``~/.bashrc`` completion.
- Add ``secureboot_signing`` role for Secure Boot MOK enrollment and kernel module signing with shared keypair support for akmods and dkms
- Add ``system_config`` and ``user_config`` roles; align roles with standard conventions; update configs
- Add playbook to update cloud CLIs
- ``openshift_local`` — optional temporary passwordless sudo for ``crc setup`` via a validated ``/etc/sudoers.d`` file that is removed afterward (``openshift_local_crc_setup_temporary_sudo``).
- add ``to_gnome_clocks`` filter plugin for generating GNOME world clock GVariant strings
- install_cloud_clis - create install_cloud_clis_bin_dir before CLI install tasks when the directory is missing
- install_cloud_clis - manage bash completion in one ``.bashrc`` block
- install_cloud_clis - remove stale AWS CLI versions after install
- install_cloud_clis role - resolve ROSA CLI latest stable from GitHub releases and download from mirror.openshift.com/pub/cgw/rosa
- system_config - Add v4l2loopback support to install ``akmod-v4l2loopback`` and configure the kernel module
- system_config - add package management with RPM Fusion repository and package installation support
- user_config role - add Python tool installation via uv
- user_config role - add VS Code and Cursor extension installation via CLI
- user_config role - add optional GNOME Shell extension installation
- user_config role - add optional uv installation via the standalone installer
- user_config role - replace hard-coded dconf tasks with the ``user_config_dconf_settings`` variable

Bugfixes
--------

- fix ansible_user_dir deprecation warnings
- fix missing directories and default bookmarks include handling
- install_cloud_clis - fix AWS CLI first-time install failure
- install_cloud_clis - guard bash completion lines in .bashrc with ``command -v`` so they are silently skipped when the CLI is not installed
- install_cloud_clis - select Tekton CLI GitHub release by highest semver among GA releases
- install_cloud_clis - select helm, kustomize, ROSA, stern, and kube-linter GitHub releases by highest semver among GA releases
- install_cloud_clis role - apply install_cloud_clis_bin_dir and install_cloud_clis_aws_install_root defaults in tasks after facts instead of argument_specs and role defaults, so validate_argument_spec works when play gather_facts is false
- use a consistent home directory and UID/GID for templated user files
