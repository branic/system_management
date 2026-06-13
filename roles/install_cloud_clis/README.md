# install_cloud_clis

Install and update common **cloud and Kubernetes CLIs** for the **user that runs this role** (the SSH connection user, or **`become_user`** when the role runs with privilege escalation):

- AWS CLI
- OpenShift CLI (`oc`) and `kubectl`
- ROSA CLI
- Tekton CLI (`tkn`)
- kube-linter
- kustomize
- stern
- Helm
- Google Workspace CLI (`gws`)

Binaries are placed under **`install_cloud_clis_bin_dir`**. If you do not set it, the role assigns **`{{ ansible_facts['user_dir'] }}/.local/bin`** after its first **`setup`** task. The AWS CLI also uses **`install_cloud_clis_aws_install_root`**; if unset, the role sets **`{{ ansible_facts['user_dir'] }}/.local/aws-cli`** when AWS tasks run.

## Requirements

- Ansible **2.16+** (see [`meta/main.yml`](meta/main.yml)).
- Outbound **HTTPS** when checking and downloading releases:
  - **GitHub** (`api.github.com`, `github.com`) — version checks and release assets for most CLIs (including gws, stern, Tekton, kube-linter, kustomize, OCM, and Helm version discovery)
  - **AWS** (`awscli.amazonaws.com`) — AWS CLI installer (tags resolved via GitHub)
  - **Helm** (`get.helm.sh`) — Helm binary download
  - **OpenShift mirrors** (`mirror.openshift.com`) — oc and rosa CLI binaries (ROSA semver candidates from GitHub; installable version is the newest GA release present on the mirror)
- Targets are **x86_64 Linux** (download URLs and archives are fixed for that architecture).

## Facts and connection

- The role **always** runs **`setup`** with a minimal subset (`!all` + `min`) as its first task so **`ansible_facts['user_dir']`** matches the **effective** user for the role (including **`become_user`**). That avoids stale `user_dir` values from an earlier play-level `gather_facts` that ran as the SSH user while the role runs as someone else.
- Default paths for those variables are applied **after** that **`setup`** (and, for **`install_cloud_clis_aws_install_root`**, at the start of AWS tasks) so templates are not evaluated before facts exist. Connect as one user and set **`become_user`** on the role if the CLIs should live in that user's home.

## Role variables

See [`defaults/main.yml`](defaults/main.yml) (component list) and [`meta/argument_specs.yml`](meta/argument_specs.yml) for the full specification.

| Variable | Description |
| --- | --- |
| `install_cloud_clis_components` | Subset of CLIs to install or update: `aws`, `oc`, `ocm`, `rosa`, `tekton`, `kube_linter`, `kustomize`, `stern`, `helm`, `gws`. |
| `install_cloud_clis_bin_dir` | Directory for symlinks/binaries. If omitted, set after **`setup`** to `{{ ansible_facts['user_dir'] }}/.local/bin`. |
| `install_cloud_clis_aws_install_root` | AWS CLI `-i` install root. If omitted, set when AWS tasks run to `{{ ansible_facts['user_dir'] }}/.local/aws-cli`. |
| `install_cloud_clis_manage_bashrc_completion` | When `true` (default), maintain a single Ansible `blockinfile` region in `~/.bashrc` for bash completion of selected CLIs. Set `false` to skip `.bashrc` edits entirely. |
| `install_cloud_clis_update_messages` | List of human-readable update messages accumulated during the run; usually leave default `[]`. |

## Dependencies

The **collection** declares a dependency on **`community.general`** (see the collection [`galaxy.yml`](../../galaxy.yml)); Tekton CLI tasks use **`community.general.version_sort`** to pick the highest semantic version among GitHub GA releases.

### ROSA CLI

- **Candidate versions** come from **non-prerelease** GitHub releases (`openshift/rosa`). The role installs the **newest GA version that is already published** on `mirror.openshift.com/pub/cgw/rosa` (probing the ten newest GitHub versions). When GitHub is ahead of the mirror, the play continues and a message notes the lag.
- A failure in one CLI component (network, mirror, or install error) is **recorded and skipped**; other components in `install_cloud_clis_components` still run.

### Tekton CLI (`tkn`)

- **Latest version** is the **highest semver** among **non-prerelease** GitHub releases returned in the first API page (`per_page=100`), not the release with the newest publish date. Tekton maintains parallel maintenance lines, so publish order and semver order can differ.
- The role **installs or upgrades** only when the target is **strictly newer** than the installed client (no downgrades).

## Example playbook

```yaml
---
- name: Update cloud CLI components
  hosts: laptop
  gather_facts: true
  roles:
    - role: branic.system_management.install_cloud_clis
```

Limit which CLIs are managed:

```yaml
---
- name: Install selected CLIs
  hosts: laptop
  gather_facts: true
  roles:
    - role: branic.system_management.install_cloud_clis
      vars:
        install_cloud_clis_components:
          - aws
          - helm
```

## Bash completion and `.bashrc`

When `install_cloud_clis_manage_bashrc_completion` is `true`, the role writes one contiguous block in **`{{ ansible_facts['user_dir'] }}/.bashrc`** between markers:

`# BEGIN ANSIBLE MANAGED BLOCK branic.system_management.install_cloud_clis` and `# END ANSIBLE MANAGED BLOCK branic.system_management.install_cloud_clis`

The block defines a **`_lazy_completion`** shell function and registers one-liner calls for each CLI. Completions are deferred until the user's first tab-complete for a given command, then cached under **`~/.cache/bash_completions/`**. The cache auto-invalidates when the CLI binary is newer than the cached file. AWS CLI uses a direct binary completer (`aws_completer`) and does not use the lazy-load mechanism. Only CLIs listed in `install_cloud_clis_components` are included.

`blockinfile` runs with **`backup: true`** (timestamped `.bashrc` backup beside the file) and sets **`mode: 0644`** on `.bashrc` when the module updates the file. Add your own completions **outside** that marked region (for example in `~/.bashrc-local` or after the block) so the role does not manage them.

If you set **`install_cloud_clis_manage_bashrc_completion: false`**, the role does not read or change `.bashrc`. Any block from an earlier run remains until you remove it manually.

## Idempotency and check mode

Version checks use `command` with `changed_when: false` where appropriate. Network-backed installs may not fully support check mode; review behavior before relying on `--check`.

## License

GPL-3.0-only — see the collection [LICENSE](../../LICENSE).

## Author

Brant Evans (see [`meta/main.yml`](meta/main.yml)).
