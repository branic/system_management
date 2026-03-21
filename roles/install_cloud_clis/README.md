# install_cloud_clis

Install and update common **cloud and Kubernetes CLIs** for the **Ansible connection user**:

- AWS CLI
- OpenShift CLI (`oc`) and `kubectl`
- ROSA CLI
- Tekton CLI (`tkn`)
- kube-linter
- kustomize
- stern
- Helm

Binaries are placed under **`install_cloud_clis_bin_dir`** (default `{{ ansible_user_dir }}/.local/bin`). The AWS CLI also uses **`install_cloud_clis_aws_install_root`** (default `{{ ansible_user_dir }}/.local/aws-cli`) for its installer layout.

## Requirements

- Ansible **2.16+** (see [`meta/main.yml`](meta/main.yml)).
- Outbound **HTTPS** to vendor endpoints (GitHub, AWS, OpenShift mirrors, Helm) when checking and downloading releases.
- Targets are **x86_64 Linux** (download URLs and archives are fixed for that architecture).

## Facts and connection

- Paths use **`ansible_user_dir`**. If `ansible_user_dir` is not already available (for example `gather_facts: false` in the play), the role runs `setup` with a minimal fact subset (`!all` + `min`) so it is defined.
- Run the play **as the user** whose home should receive the CLIs (`ansible_user` / remote user). This role is not aimed at `become: true` as root while configuring another user’s home unless you set facts accordingly.

## Role variables

See [`defaults/main.yml`](defaults/main.yml) and [`meta/argument_specs.yml`](meta/argument_specs.yml) for the full specification.

| Variable | Description |
| --- | --- |
| `install_cloud_clis_components` | Subset of CLIs to install or update: `aws`, `oc`, `rosa`, `tekton`, `kube_linter`, `kustomize`, `stern`, `helm`. |
| `install_cloud_clis_bin_dir` | Directory for symlinks/binaries (default `{{ ansible_user_dir }}/.local/bin`). |
| `install_cloud_clis_aws_install_root` | AWS CLI `-i` install root (default `{{ ansible_user_dir }}/.local/aws-cli`). |
| `install_cloud_clis_update_messages` | List of human-readable update messages accumulated during the run; usually leave default `[]`. |

## Dependencies

None.

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

## Idempotency and check mode

Version checks use `command` with `changed_when: false` where appropriate. Network-backed installs may not fully support check mode; review behavior before relying on `--check`.

## License

GPL-3.0-only — see the collection [LICENSE](../../LICENSE).

## Author

Brant Evans (see [`meta/main.yml`](meta/main.yml)).
