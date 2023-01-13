# install_cloud_clis

This role will install and update the following Cloud CLIs:

- AWS
- OpenShift
- ROSA

The CLIs are installed into `$HOME/.local/bin` directory.

## Requirements

None

## Role Variables

None

## Dependencies

None

## Example Playbook

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

```yml
---
- name: Update Cloud CLI components
  hosts: laptop
  gather_facts: false

  tasks:
    - name: Include Install CLIs role
      ansible.builtin.include_role:
        name: install_cloud_clis
```

## License

MIT

## Author Information

Brant Evans
