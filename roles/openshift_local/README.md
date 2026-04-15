# openshift_local

Installs or upgrades **OpenShift Local** (the `crc` CLI) for the **user that runs this role** (the SSH connection user, or **`become_user`** when the role runs with privilege escalation).

The role compares the **GitHub** latest release tag with the installed `crc version`, downloads the matching **Linux** archive from the **Red Hat mirror** when an install or upgrade is needed, runs **`crc delete`** (confirming the prompt) and **`crc setup`**, optionally removes **stale** `.crcbundle` files under the cache path reported by `crc setup`, and can maintain **bash completion** in `~/.bashrc`.

## Requirements

- Ansible **2.16+** (see [`meta/main.yml`](meta/main.yml)).
- Collection dependency **`community.general`** (for `community.general.expect` when running `crc delete`).
- **`pexpect`** on the managed host (Python library used by the expect module).
- Outbound **HTTPS** to GitHub and Red Hat mirror endpoints.
- Target **Linux** on **x86_64** or **aarch64** (archive names `crc-linux-amd64.tar.xz` and `crc-linux-arm64.tar.xz`).

## Facts and connection

- The role **always** runs **`setup`** with a minimal subset (`!all` + `min`) first so **`ansible_facts['user_dir']`** matches the effective user (including **`become_user`**).
- Default **`openshift_local_bin_dir`** is **`{{ ansible_facts['user_dir'] }}/.local/bin`** when unset.

## Role variables

See [`defaults/main.yml`](defaults/main.yml) and [`meta/argument_specs.yml`](meta/argument_specs.yml).

| Variable | Description |
| --- | --- |
| `openshift_local_bin_dir` | Directory for the `crc` binary. Default: `~/.local/bin` after setup. |
| `openshift_local_manage_bashrc_completion` | When `true` (default), manage a `blockinfile` region in `~/.bashrc` for `crc completion bash`. |
| `openshift_local_crc_github_releases_api` | GitHub API URL for the latest release (used for version comparison). |
| `openshift_local_crc_download_base` | Base URL for the `crc-linux-<arch>.tar.xz` archive under the Red Hat mirror. |

## Example playbook

```yaml
---
- name: Update OpenShift Local
  hosts: laptop
  gather_facts: false
  roles:
    - role: branic.system_management.openshift_local
```

Using the collection playbook (from a checkout with `ANSIBLE_COLLECTIONS_PATH` set):

```bash
ansible-playbook playbooks/openshift_local.yml -i laptop, -e target=laptop
```

## Bash completion

When `openshift_local_manage_bashrc_completion` is `true`, the role writes a block in **`{{ ansible_facts['user_dir'] }}/.bashrc`** between markers:

`# BEGIN ANSIBLE MANAGED BLOCK branic.system_management.openshift_local` and `# END ANSIBLE MANAGED BLOCK branic.system_management.openshift_local`

The block is refreshed in an **`always`** phase so completion is updated even if an install task fails (aligned with `install_cloud_clis`).
