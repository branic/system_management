# secureboot_signing

Configures **Secure Boot kernel module signing** on Fedora Linux by generating
a shared x509 signing keypair, enrolling it as a Machine Owner Key (MOK), and
configuring **akmods** and/or **dkms** to use the key for automatic module
signing.

## How it works

Third-party kernel modules (e.g. `akmod-v4l2loopback`, NVIDIA drivers) are
rejected by the kernel when Secure Boot is enabled unless they are signed with
a trusted key. This role:

1. Generates a single signing keypair under `/etc/pki/secureboot/`.
2. Stages the public certificate for MOK enrollment via `mokutil --import`.
3. Configures akmods and dkms to reference the shared key through symlinks so
   both tools sign modules with the same MOK-enrolled certificate.

A **single shared key** is used for all tools because:

- Both akmods and dkms serve the same purpose (signing locally-built modules).
- One key means one MOK enrollment and one reboot, not two.
- The security boundary is identical (same host, same trust model).

### Key paths

| Path | Purpose |
| --- | --- |
| `/etc/pki/secureboot/private/secureboot_signing_key.priv` | Shared private key |
| `/etc/pki/secureboot/certs/secureboot_signing_cert.der` | Shared public certificate (DER) |
| `/etc/pki/akmods/private/private_key.priv` | Symlink to shared private key |
| `/etc/pki/akmods/certs/public_key.der` | Symlink to shared certificate |
| `/var/lib/dkms/mok.key` | Symlink to shared private key |
| `/var/lib/dkms/mok.pub` | Symlink to shared certificate |

## Two-phase workflow

This role is designed to run **before** any role that installs akmod or dkms
packages (e.g. `system_config`). The workflow has two phases:

**Phase 1** &mdash; Run this role to set up signing infrastructure and stage
MOK enrollment. Then reboot and complete enrollment in the UEFI MOK Manager.

**Phase 2** &mdash; Run `system_config` (or equivalent) to install akmod/dkms
packages. The modules are built, signed with the now-trusted key, and load
normally.

On subsequent runs after MOK enrollment, both roles are idempotent no-ops for
the signing-related tasks.

## Requirements

- Ansible **2.16+** (see `meta/main.yml`).
- Target must be a **Fedora Linux** system with UEFI Secure Boot enabled.

## Role variables

See `defaults/main.yml` and `meta/argument_specs.yml` for the full
specification.

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `secureboot_signing_mok_password` | yes | &mdash; | Temporary password for `mokutil --import` and the UEFI MOK Manager screen. Must be vault-encrypted. |
| `secureboot_signing_modules` | no | `["akmods", "dkms"]` | Which module-building tools to configure. Supported: `akmods`, `dkms`. |

## MOK enrollment (manual, one-time)

After the first playbook run you must complete enrollment at the UEFI console:

1. Reboot the system.
2. At the blue **MOK Manager** screen select **Enroll MOK**.
3. Select **Continue**, then **Yes**.
4. Enter the same password you provided in `secureboot_signing_mok_password`.
5. Select **Reboot**.

After this one-time step, akmods and dkms will automatically sign modules on
every kernel update using the enrolled key.

## Dependencies

None.

## Example playbook

```yaml
---
- name: Configure Secure Boot signing and system packages
  hosts: workstations
  gather_facts: false
  roles:
    - role: branic.system_management.secureboot_signing
      become: true
      vars:
        secureboot_signing_mok_password: "{{ vault_secureboot_mok_password }}"

    - role: branic.system_management.system_config
      become: true
      vars:
        system_config_packages:
          - akmod-v4l2loopback
```

To configure only akmods (skip dkms):

```yaml
- role: branic.system_management.secureboot_signing
  become: true
  vars:
    secureboot_signing_mok_password: "{{ vault_secureboot_mok_password }}"
    secureboot_signing_modules:
      - akmods
```

## Idempotency

- Key generation uses `creates:` and is skipped when the keypair already
  exists.
- MOK import is skipped when `mokutil --test-key` confirms the key is
  already enrolled.
- Symlinks report no change when they already point to the correct target.
- Safe to re-run at any time.

## License

GPL-3.0-only &mdash; see the collection [LICENSE](../../LICENSE).

## Author

Brant Evans (see `meta/main.yml`).
