# system_config

System-wide configuration for **Fedora Linux**-style hosts:

- **RPM Fusion** repository enablement (free, nonfree, or both)
- **DNF repositories** and **COPR repositories**
- **DNF packages** (installed via `dnf5`)
- local **groups** and **users**
- **Flatpak**
  - **Flathub** remote
  - installation of a configurable set of **Flatpak** applications.

## Requirements

- Ansible **2.16+** (see `meta/main.yml`).
- Collections:
  - **community.general**

## Role variables

See `defaults/main.yml` and `meta/argument_specs.yml` for the full specification.

| Variable | Description |
| --- | --- |
| `system_config_rpmfusion` | Enable RPM Fusion repositories: `none` (default), `free`, `nonfree`, or `both`. |
| `system_config_dnf_repositories` | List of DNF repository definitions: `name` and `description` (required); optional `baseurl`, `metalink`, `gpgcheck`, `gpgkey`, `repo_gpgcheck`, `enabled`, `state`. |
| `system_config_copr_repositories` | List of COPR repository definitions: `name` in `owner/project` format (required); optional `state` (`enabled` / `disabled` / `absent`). |
| `system_config_packages` | List of package names to install via DNF. |
| `system_config_flatpak_packages` | List of Flatpak application IDs to install |
| `system_config_groups` | Optional list of group definitions: `name` (required), optional `gid`, `system`. |
| `system_config_users` | Optional list of user definitions: `name` (required); optional `uid`, `comment`, `groups`, `shell`, `system`, `create_home`, `password`, `update_password` (`on_create` / `always`). |

Omit `groups` on a user entry if that user should not receive secondary groups via this task's `groups` parameter.

## Dependencies

None.

## Example playbook

```yaml
---
- name: Configure system packages and accounts
  hosts: workstations
  become: true
  roles:
    - role: branic.system_management.system_config
```

With variables:

```yaml
---
- name: Configure system
  hosts: workstations
  become: true
  roles:
    - role: branic.system_management.system_config
      vars:
        system_config_dnf_repositories:
          - name: example-repo
            description: Example Repository
            baseurl: https://example.com/repo/$releasever/$basearch
            gpgcheck: true
            gpgkey: https://example.com/RPM-GPG-KEY-example
        system_config_copr_repositories:
          - name: user/project
        system_config_packages:
          - vim-enhanced
          - htop
          - tmux
        system_config_flatpak_packages:
          - org.videolan.VLC
        system_config_groups:
          - name: developers
        system_config_users:
          - name: deploy
            groups:
              - developers
            shell: /bin/bash
```

## Idempotency and check mode

Repository, package, group, user, and Flatpak remote tasks are intended to be idempotent. DNF package installs use `state: present`; Flatpak installs use `state: latest` -- review whether that matches your change expectations.

## License

GPL-3.0-only — see the collection [LICENSE](../../LICENSE).

## Author

Brant Evans (see `meta/main.yml`).
