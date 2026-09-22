# manage_bash_completions

Maintain a shared **lazy-loaded bash completion** section in the connection user's **`~/.bashrc`**.

This role is a **generic executor**. It does not own a catalog of CLIs. Consumer roles pass provider-scoped completion metadata when calling it with `include_role`.

## Role variables

See [`meta/argument_specs.yml`](meta/argument_specs.yml).

| Variable | Required | Description |
| --- | --- | --- |
| `manage_bash_completions_provider_cmds` | yes | All command names this provider may manage. |
| `manage_bash_completions_entries` | yes | Structured completion entries to register on this run. |
| `manage_bash_completions_enabled` | no | Overall enable flag (default `true`). |
| `manage_bash_completions_path` | no | Target bashrc path (default `{{ ansible_facts['user_dir'] }}/.bashrc`). |

### Entry schema

```yaml
# direct completer
- cmd: aws
  type: direct
  completer: /home/user/.local/bin/aws_completer

# lazy generator
- cmd: oc
  type: lazy
  generator: [oc, completion, bash]
```

## Example usage

```yaml
- name: Refresh bash completions
  ansible.builtin.include_role:
    name: manage_bash_completions
  vars:
    manage_bash_completions_provider_cmds: [aws, oc, helm]
    manage_bash_completions_entries:
      - cmd: aws
        type: direct
        completer: "{{ install_cloud_clis_bin_dir }}/aws_completer"
      - cmd: oc
        type: lazy
        generator: [oc, completion, bash]
```

## Behavior

- Ensures a canonical `_lazy_completion()` helper exists under the anchor comment `# Lazy-load and cache bash completions on first use`.
- Merges caller entries while preserving completion lines owned by other providers.
- Renders completion lines in stable alphabetical order by command name.
- Removes legacy Ansible `blockinfile` markers and obsolete one-line `source <(...)` completion registrations.
- Inserts the section before a `~/.bashrc-local` stanza when no anchored section exists yet; otherwise appends to EOF.

## License

GPL-3.0-only — see the collection [LICENSE](../../LICENSE).

## Author

Brant Evans (see [`meta/main.yml`](meta/main.yml)).
