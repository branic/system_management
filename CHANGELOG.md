# Branic System Management Collection Release Notes

**Topics**

- <a href="#v1-0-0">v1\.0\.0</a>
    - <a href="#release-summary">Release Summary</a>
    - <a href="#minor-changes">Minor Changes</a>
    - <a href="#bugfixes">Bugfixes</a>

<a id="v1-0-0"></a>
## v1\.0\.0

<a id="release-summary"></a>
### Release Summary

Initial release of the collection

<a id="minor-changes"></a>
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
