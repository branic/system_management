# user_config

Configure per-user desktop settings for the **user that runs this role** (the SSH connection user, or **`become_user`** when the role runs with privilege escalation):

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

- The role **always** runs **`setup`** with a minimal subset (`!all` + `min`) as its first task so **`ansible_facts['user_dir']`** matches the **effective** user for the role (including **`become_user`**). That avoids stale `user_dir` values from an earlier play-level `gather_facts` that ran as the SSH user while the role runs as someone else.
- Paths use **`ansible_facts['user_dir']`**. File **`owner`** / **`group`** use **`ansible_facts['user_id']`** and **`ansible_facts['user_gid']`** (same minimal `setup` as `user_dir`), so ownership matches the **effective** user (including **`become_user`**), not the SSH connection user.
- Using **`become_user`** (for example connect as `ansible`, become `brant`) is supported for targeting that user's home. Arbitrary `become` to root while configuring another account without **`become_user`** is still not what this role assumes.

## Role variables

See `defaults/main.yml` and `meta/argument_specs.yml` for the full specification.

| Variable | Description |
| --- | --- |
| `user_config_slack_flatpak_sockets` | If `true` (default), write Slack Flatpak socket overrides (system/session bus, Wayland; not X11). |
| `user_config_slack_flatpak_filesystems` | Extra filesystem entries for the Slack override (list of strings); if empty, the `filesystems` line is omitted. |
| `user_config_gtk_include_default_bookmarks` | If `true` (default), prepend GNOME-style XDG default bookmarks (`Documents`, `Downloads`, etc.) before `user_config_gtk_bookmarks`. Set `false` to manage only your explicit list. |
| `user_config_gtk_bookmarks` | List of `path` (required) and optional `name` for GTK 3 `~/.config/gtk-3.0/bookmarks`. Paths may be `file://`, absolute, `~`, `~/`, or relative to the user home. |
| `user_config_dconf_settings` | Dconf settings to apply. List of dicts with `key` (required), `value` (GVariant string, required when state is `present`), and optional `state` (`present` or `absent`, default `present`). |
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
