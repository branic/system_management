# user_config

Configure per-user desktop settings for the **Ansible connection user**:

- GTK 3 sidebar bookmarks
- Slack Flatpak overrides
- GNOME DConf keys
- GNOME Shell extensions

## Requirements

- Ansible **2.16+** (see `meta/main.yml`).
- Collection **community.general** (DConf, templates; Flatpak-related paths are file-based).
- Target systems must provide **`gnome-extensions`** (typically from the `gnome-shell` package) for GNOME Shell extensions.
- Target systems where these settings apply (typically **Fedora** with GNOME).

## Facts and connection

- Paths use **`ansible_facts['user_dir']`** (and `owner` / `group` from **`ansible_user`**). If `user_dir` is not in **`ansible_facts`** (for example `gather_facts: false` in the play), the role runs `setup` with a minimal fact subset to define it.
- Run the play **as the user** whose home you are configuring (`ansible_user` / remote user). Using `become` to root and a different login user is not what this role is written for unless you also set facts accordingly.

## Role variables

See `defaults/main.yml` and `meta/argument_specs.yml` for the full specification.

| Variable | Description |
| --- | --- |
| `user_config_slack_flatpak_sockets` | If `true` (default), write Slack Flatpak socket overrides (system/session bus, Wayland; not X11). |
| `user_config_slack_flatpak_filesystems` | Extra filesystem entries for the Slack override (list of strings); if empty, the `filesystems` line is omitted. |
| `user_config_gtk_include_default_bookmarks` | If `true` (default), prepend GNOME-style XDG default bookmarks (`Documents`, `Downloads`, etc.) before `user_config_gtk_bookmarks`. Set `false` to manage only your explicit list. |
| `user_config_gtk_bookmarks` | List of `path` (required) and optional `name` for GTK 3 `~/.config/gtk-3.0/bookmarks`. Paths may be `file://`, absolute, `~`, `~/`, or relative to the user home. |
| `user_config_gnome_extensions` | GNOME Shell extensions to install. Each entry is a **dict** with at least one of `url` (direct HTTPS URL to the extension zip), `id` (extensions.gnome.org pk), or `name` (exact catalog name to search). Precedence is `url`, then `id`, then `name`. Optional `force` (pass `-f` to `gnome-extensions install`), optional `enable` (default `true`: `gnome-extensions enable`, or `disable` when `false`). Requires `gnome-extensions` and `gnome-shell` on the target. Bundles are downloaded to a **temporary directory** that is removed when extension tasks finish. |

## Dependencies

None.

## Example playbook

```yaml
---
- name: Apply user desktop preferences
  hosts: workstations
  gather_facts: true
  roles:
    - role: branic.system_management.user_config
```

With variables:

```yaml
---
- name: Apply user desktop preferences
  hosts: workstations
  gather_facts: true
  roles:
    - role: branic.system_management.user_config
      vars:
        user_config_gtk_bookmarks:
          - path: "~/Documents"
            name: Documents
        user_config_slack_flatpak_sockets: true
```

## Idempotency and check mode

Tasks use modules and templates where possible for idempotent behavior. Review community.general behavior for DConf and your environment if you rely on check mode.

## License

GPL-3.0-only — see the collection [LICENSE](../../LICENSE).

## Author

Brant Evans (see `meta/main.yml`).
