# branic.system_management.openshift_local

Installs or upgrades **OpenShift Local** (the `crc` CLI) for the **user that runs this role** (the SSH connection user, or **`become_user`** when the role runs with privilege escalation).

The role resolves a **target** CRC version from **GitHub** (either the newest release or a **pinned** `openshift_local_crc_version`), compares it with the installed `crc version`, downloads the matching **Linux** archive from the **Red Hat mirror** under `.../clients/crc/<semver>/` when the binary is missing or outdated, reconciles **`crc` configuration** from a single dictionary variable, runs **`crc delete --force`** (non-interactive) and **`crc setup`** when anything needs to change, optionally removes **stale** `.crcbundle` files under the cache path reported by `crc setup`, and can maintain **bash completion** in `~/.bashrc`.

See [Configuring CRC](https://crc.dev/docs/configuring/) for upstream property names and semantics.

## Requirements

- Ansible **2.16+** (see [`meta/main.yml`](meta/main.yml)).
- This role uses **`ansible.builtin`** modules only; it does not add Python library requirements beyond what your Ansible install already provides.
- The **system_management** collection may list other collection dependencies in **`galaxy.yml`** for the collection as a whole; nothing beyond **`ansible.builtin`** is required specifically to run this role.
- Outbound **HTTPS** to GitHub and Red Hat mirror endpoints.
- Target **Linux** on **x86_64** or **aarch64** (archive names `crc-linux-amd64.tar.xz` and `crc-linux-arm64.tar.xz`).
- With the default **`openshift_local_crc_setup_temporary_sudo`**, the play (or role) must allow **privilege escalation** (**`become`**) so Ansible can create and delete the temporary **`sudoers.d`** fragment before and after **`crc setup`**. Not required when that variable is **`false`** and you do not rely on other role tasks that need **`become`** (for example **`openshift_local_install_host_packages`**).

## Facts and connection

- The role runs **`ansible.builtin.setup`** with subsets **`!all`**, **`min`**, **`hardware`**, and **`virtual`** so host CPU, memory, and disk checks work and **`ansible_facts['user_dir']`** matches the effective user (including **`become_user`**).
- **`openshift_local_bin_dir`** defaults to **`~/.local/bin`**. Set it to install the binary elsewhere.

## CRC version selection

- **`openshift_local_crc_version`** (default **empty**): When **empty** or unset, the role uses the **newest** CRC release returned by GitHub's releases API. When set to **`X.Y.Z`** or **`vX.Y.Z`** (digits only in each segment), the role installs that release only. The value is **validated** with a strict pattern before any GitHub or mirror URL is built; invalid values fail immediately with a clear message. A version that does not exist on GitHub causes the **`releases/tags/...`** request to fail (for example HTTP 404).
- The **`crc` Linux tarball** is fetched from the Red Hat mirror at **`.../openshift-v4/clients/crc/<semver>/crc-linux-<arch>.tar.xz`**, where **`<semver>`** matches the GitHub tag (without a leading **`v`**). If a tag is very new, the mirror may lag GitHub briefly; in that case **`ansible.builtin.unarchive`** can fail until the artifact is published.

## Host prerequisites and resources

- **Fedora / RHEL family:** The role always checks the required RPM list in [`vars/main.yml`](vars/main.yml). If **`openshift_local_install_host_packages`** is `true`, it runs **`dnf`** with **`state: present`** (idempotent, so already-installed packages are left alone). It then **refreshes package facts** and **asserts** every required package is present, so verification always reflects the system after any install, and the install path cannot pass while facts still show missing packages.
- **Other OS families:** Package tasks are skipped (optional debug at verbosity 1).
- **All targets:** The role **fails** if the host does not meet **preset-based** CPU, RAM, and free disk minimums (see [`vars/main.yml`](vars/main.yml) and [CRC system requirements](https://crc.dev/docs/using/)). The effective preset defaults to **`openshift`** when **`openshift_local_crc_config.preset`** is unset.
- If **`openshift_local_crc_config`** sets **`cpus`**, **`memory`**, or **`disk-size`**, those values must be **greater than or equal to** the CRC-documented minimums for the selected preset (same tables in [`vars/main.yml`](vars/main.yml)). Free space on the filesystem that contains **`user_dir`** (from **`df`**) must be at least the **maximum** of the preset's host disk minimum and any configured **`disk-size`** (GiB).

## CRC configuration (single dictionary)

- **`openshift_local_crc_config`** (default **`{}`**) is the only user-facing surface for **`crc config`** keys (`preset`, `cpus`, `memory`, `disk-size`, `consent-telemetry`, `skip-check-*`, and any future keys). Add or remove keys in inventory without changing role code.
- The role builds an **effective** config by applying default **`preset: openshift`** only when **`preset`** is absent, so validation and host checks have a defined preset. Other keys are enforced only when you set them.
- When the `crc` binary is present, the role compares each desired key to **`crc config get <key>`** (including default values reported by the CLI) and runs **`crc config set`** only for keys that still differ.

## Reconcile behavior

The role performs a full reconcile when **any** of the following is true:

- The **`crc`** binary is missing, or its version does not match the **target** version from GitHub.
- Any key in the effective desired config **differs** from the live configuration.

When reconcile is required, the role:

1. **Unarchives** the binary only if it is missing or outdated.
2. Runs **`crc delete --force`** (benign exit codes when no instance exists are allowed).
3. Applies **`crc config set`** for keys that still need to change.
4. When **`openshift_local_crc_setup_temporary_sudo`** is **`true`** (default), installs a temporary **`/etc/sudoers.d`** fragment (validated with **`visudo`**) so the connection user can run **`sudo`** without a password during **`crc setup`**, then removes that file afterward (even if **`crc setup`** fails). Those two tasks use privilege escalation (**`become`**). Set **`openshift_local_crc_setup_temporary_sudo`** to **`false`** if the user already has passwordless **`sudo`** or you manage **`sudoers`** elsewhere. Override the path with **`openshift_local_crc_setup_sudoers_path`** if needed (default: **`/etc/sudoers.d/99-crc-setup-<username>`**).
5. Runs **`crc setup`** (as the connection user; **`crc`** invokes **`sudo`** internally where required).
6. Prunes stale bundle caches (same heuristics as before).

When the binary is current **and** configuration matches, the role skips unarchive, delete, `crc config set`, and **`crc setup`**.

## Role variables

See [`defaults/main.yml`](defaults/main.yml) and [`meta/argument_specs.yml`](meta/argument_specs.yml).

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `openshift_local_bin_dir` | No | `~/.local/bin` | Directory for the `crc` binary. |
| `openshift_local_crc_version` | No | `""` | Pin CRC to `X.Y.Z` or `vX.Y.Z`, or leave empty for newest GitHub release (validated before URLs are built). |
| `openshift_local_crc_config` | No | `{}` | Dict of desired `crc config` keys and values. |
| `openshift_local_install_host_packages` | No | `false` | When `false`, only verify required host packages are installed. When `true`, install them if needed (requires privilege escalation). Only Fedora/RHEL supported. |
| `openshift_local_crc_setup_temporary_sudo` | No | `true` | When `true`, before **`crc setup`** the role writes a validated temporary **`sudoers.d`** file granting the connection user passwordless **`sudo`**, then deletes it afterward. Requires privilege escalation for those tasks. Use `false` if passwordless **`sudo`** is already configured. |
| `openshift_local_crc_setup_sudoers_path` | No | unset | Optional absolute path for that temporary file. If unset, defaults to **`/etc/sudoers.d/99-crc-setup-<connection username>`**. |
| `openshift_local_manage_bashrc_completion` | No | `true` | When `true`, maintain `crc` tab completion in the connection user's `~/.bashrc`. |

## Example playbook

```yaml
---
- name: Update OpenShift Local
  hosts: laptop
  gather_facts: false
  roles:
    - role: branic.system_management.openshift_local
      vars:
        openshift_local_crc_version: "2.58.0"
        openshift_local_crc_config:
          preset: openshift
          cpus: 4
          memory: 10752
          consent-telemetry: "no"
```

Using the collection playbook (from a checkout with `ANSIBLE_COLLECTIONS_PATH` set):

```bash
ansible-playbook playbooks/openshift_local.yml -i laptop, -e target=laptop
```

## Bash completion

When `openshift_local_manage_bashrc_completion` is `true`, the role writes a block in **`{{ ansible_facts['user_dir'] }}/.bashrc`** between markers:

`# BEGIN ANSIBLE MANAGED BLOCK branic.system_management.openshift_local` and `# END ANSIBLE MANAGED BLOCK branic.system_management.openshift_local`

The block is refreshed in an **`always`** phase so completion is updated even if an install task fails (aligned with `install_cloud_clis`).
