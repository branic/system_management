# Branic System Management Collection Release Notes

**Topics**

- <a href="#v1-1-0">v1\.1\.0</a>
    - <a href="#release-summary">Release Summary</a>
    - <a href="#minor-changes">Minor Changes</a>
- <a href="#v1-0-0">v1\.0\.0</a>
    - <a href="#release-summary-1">Release Summary</a>
    - <a href="#minor-changes-1">Minor Changes</a>
    - <a href="#bugfixes">Bugfixes</a>

<a id="v1-1-0"></a>
## v1\.1\.0

<a id="release-summary"></a>
### Release Summary

Feature release adding systemd unit management\, sysctl configuration\, and package replacement capabilities\.

<a id="minor-changes"></a>
### Minor Changes

* Add <code>ansible\.posix</code> collection dependency\.
* Normalize role <code>meta/main\.yml</code>\; <code>version\_added\: 1\.0\.0</code> on argument specs\.
* openshift\_local \- add optional <code>openshift\_local\_crc\_version</code> to pin a CRC release \(validated before download\)\.
* system\_config and user\_config roles can manage systemd units \(system and user scope\)\.
* system\_config role — add <code>system\_config\_package\_replacements</code> for <code>dnf swap</code> pairs \(optional <code>allowerasing</code>\)\, running after repo setup and before DNF package install\.
* system\_config role — add sysctl configuration support\.

<a id="v1-0-0"></a>
## v1\.0\.0

<a id="release-summary-1"></a>
### Release Summary

Initial release of the collection

<a id="minor-changes-1"></a>
### Minor Changes

* Add <code>openshift\_local</code> role to install or upgrade OpenShift Local \(CRC\) with optional host checks\, configurable <code>crc</code> settings\, and <code>\~/\.bashrc</code> completion\.
* Add <code>secureboot\_signing</code> role for Secure Boot MOK enrollment and kernel module signing with shared keypair support for akmods and dkms
* Add <code>system\_config</code> and <code>user\_config</code> roles\; align roles with standard conventions\; update configs
* Add playbook to update cloud CLIs
* <code>openshift\_local</code> — optional temporary passwordless sudo for <code>crc setup</code> via a validated <code>/etc/sudoers\.d</code> file that is removed afterward \(<code>openshift\_local\_crc\_setup\_temporary\_sudo</code>\)\.
* add <code>to\_gnome\_clocks</code> filter plugin for generating GNOME world clock GVariant strings
* install\_cloud\_clis \- create install\_cloud\_clis\_bin\_dir before CLI install tasks when the directory is missing
* install\_cloud\_clis \- manage bash completion in one <code>\.bashrc</code> block
* install\_cloud\_clis \- remove stale AWS CLI versions after install
* install\_cloud\_clis role \- resolve ROSA CLI latest stable from GitHub releases and download from mirror\.openshift\.com/pub/cgw/rosa
* system\_config \- Add v4l2loopback support to install <code>akmod\-v4l2loopback</code> and configure the kernel module
* system\_config \- add package management with RPM Fusion repository and package installation support
* user\_config role \- add Python tool installation via uv
* user\_config role \- add VS Code and Cursor extension installation via CLI
* user\_config role \- add optional GNOME Shell extension installation
* user\_config role \- add optional uv installation via the standalone installer
* user\_config role \- replace hard\-coded dconf tasks with the <code>user\_config\_dconf\_settings</code> variable

<a id="bugfixes"></a>
### Bugfixes

* fix ansible\_user\_dir deprecation warnings
* fix missing directories and default bookmarks include handling
* install\_cloud\_clis \- fix AWS CLI first\-time install failure
* install\_cloud\_clis \- guard bash completion lines in \.bashrc with <code>command \-v</code> so they are silently skipped when the CLI is not installed
* install\_cloud\_clis \- select Tekton CLI GitHub release by highest semver among GA releases
* install\_cloud\_clis \- select helm\, kustomize\, ROSA\, stern\, and kube\-linter GitHub releases by highest semver among GA releases
* install\_cloud\_clis role \- apply install\_cloud\_clis\_bin\_dir and install\_cloud\_clis\_aws\_install\_root defaults in tasks after facts instead of argument\_specs and role defaults\, so validate\_argument\_spec works when play gather\_facts is false
* use a consistent home directory and UID/GID for templated user files
