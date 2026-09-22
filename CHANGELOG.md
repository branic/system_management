# Branic System Management Collection Release Notes

**Topics**

- <a href="#v1-4-0">v1\.4\.0</a>
    - <a href="#release-summary">Release Summary</a>
    - <a href="#minor-changes">Minor Changes</a>
    - <a href="#bugfixes">Bugfixes</a>
- <a href="#v1-3-0">v1\.3\.0</a>
    - <a href="#release-summary-1">Release Summary</a>
    - <a href="#minor-changes-1">Minor Changes</a>
- <a href="#v1-2-0">v1\.2\.0</a>
    - <a href="#release-summary-2">Release Summary</a>
    - <a href="#minor-changes-2">Minor Changes</a>
    - <a href="#bugfixes-1">Bugfixes</a>
- <a href="#v1-1-0">v1\.1\.0</a>
    - <a href="#release-summary-3">Release Summary</a>
    - <a href="#minor-changes-3">Minor Changes</a>
- <a href="#v1-0-0">v1\.0\.0</a>
    - <a href="#release-summary-4">Release Summary</a>
    - <a href="#minor-changes-4">Minor Changes</a>
    - <a href="#bugfixes-2">Bugfixes</a>

<a id="v1-4-0"></a>
## v1\.4\.0

<a id="release-summary"></a>
### Release Summary

Adds a dedicated manage\_bash\_completions role and merge\_bashrc\_completions
filter plugin for shared\, lazy\-loaded bash completion management in
<code>\~/\.bashrc</code>\, replacing per\-role template handling\.

<a id="minor-changes"></a>
### Minor Changes

* Add <code>manage\_bash\_completions</code> role to maintain a shared lazy\-loaded bash completion section in <code>\~/\.bashrc</code>\, replacing per\-role template management\.
* Add <code>merge\_bashrc\_completions</code> filter plugin for idempotent merging of provider\-scoped bash completion entries with legacy format migration\.
* install\_cloud\_clis and openshift\_local roles now delegate bash completion management to the shared <code>manage\_bash\_completions</code> role\.

<a id="bugfixes"></a>
### Bugfixes

* merge\_bashrc\_completions filter plugin \-\- fix legacy one\-liner regex patterns that contained a stray <code>\></code> after the closing parenthesis\, preventing removal of old <code>source \<\(cmd completion bash\)</code> lines during migration\.
* openshift\_local \-\- update CRC binary download URL to use the current Red Hat content\-gateway path\, fixing HTTP 404 errors when installing or upgrading CRC\.

<a id="v1-3-0"></a>
## v1\.3\.0

<a id="release-summary-1"></a>
### Release Summary

Improved shell startup performance by lazy\-loading and caching bash
completions in the install\_cloud\_clis role\.

<a id="minor-changes-1"></a>
### Minor Changes

* install\_cloud\_clis \- lazy\-load and cache bash completions to eliminate subprocess spawns at shell startup

<a id="v1-2-0"></a>
## v1\.2\.0

<a id="release-summary-2"></a>
### Release Summary

Extends install\_cloud\_clis with OCM and Google Workspace CLIs\, hardens ROSA
installs against mirror lag\, and isolates per\-CLI failures\.

<a id="minor-changes-2"></a>
### Minor Changes

* install\_cloud\_clis role \- add Google Workspace CLI \(gws\) installation from GitHub releases
* install\_cloud\_clis role \- add OCM CLI \(openshift\-online/ocm\-cli\) installation support with bash completion
* install\_cloud\_clis role \- isolate each CLI install in block/rescue so one component failure does not block remaining installs
* install\_cloud\_clis role \- loop CLI installs from install\_cloud\_clis\_cli\_installers to reduce duplicated task definitions in main\.yml

<a id="bugfixes-1"></a>
### Bugfixes

* install\_cloud\_clis role \- resolve ROSA CLI install version from mirror\.openshift\.com availability so a GitHub release ahead of the mirror does not fail the play

<a id="v1-1-0"></a>
## v1\.1\.0

<a id="release-summary-3"></a>
### Release Summary

Feature release adding systemd unit management\, sysctl configuration\, and package replacement capabilities\.

<a id="minor-changes-3"></a>
### Minor Changes

* Add <code>ansible\.posix</code> collection dependency\.
* Normalize role <code>meta/main\.yml</code>\; <code>version\_added\: 1\.0\.0</code> on argument specs\.
* openshift\_local \- add optional <code>openshift\_local\_crc\_version</code> to pin a CRC release \(validated before download\)\.
* system\_config and user\_config roles can manage systemd units \(system and user scope\)\.
* system\_config role — add <code>system\_config\_package\_replacements</code> for <code>dnf swap</code> pairs \(optional <code>allowerasing</code>\)\, running after repo setup and before DNF package install\.
* system\_config role — add sysctl configuration support\.

<a id="v1-0-0"></a>
## v1\.0\.0

<a id="release-summary-4"></a>
### Release Summary

Initial release of the collection

<a id="minor-changes-4"></a>
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

<a id="bugfixes-2"></a>
### Bugfixes

* fix ansible\_user\_dir deprecation warnings
* fix missing directories and default bookmarks include handling
* install\_cloud\_clis \- fix AWS CLI first\-time install failure
* install\_cloud\_clis \- guard bash completion lines in \.bashrc with <code>command \-v</code> so they are silently skipped when the CLI is not installed
* install\_cloud\_clis \- select Tekton CLI GitHub release by highest semver among GA releases
* install\_cloud\_clis \- select helm\, kustomize\, ROSA\, stern\, and kube\-linter GitHub releases by highest semver among GA releases
* install\_cloud\_clis role \- apply install\_cloud\_clis\_bin\_dir and install\_cloud\_clis\_aws\_install\_root defaults in tasks after facts instead of argument\_specs and role defaults\, so validate\_argument\_spec works when play gather\_facts is false
* use a consistent home directory and UID/GID for templated user files
