# Branic System Management Collection

This repository contains the `branic.system_management` Ansible Collection.

Fedora Linux system configuration and management.

<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.16.0**.

For collections that support Ansible 2.9, please ensure you update your `network_os` to use the
fully qualified collection name (for example, `cisco.ios.ios`).
Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
<!--end requires_ansible-->

## External requirements

Some modules and plugins require external libraries. Please check the requirements for each plugin or module you use in the documentation to find out which requirements are needed.

When you install this collection with Ansible Galaxy, declared dependencies are installed as well. This collection depends on **`ansible.posix` >=1.5.0** and **`community.general` >=8.0.0** (see `galaxy.yml`).

## Included content

<!--start collection content-->

### Roles

| Role                                                       | Summary                                                          |
| ---------------------------------------------------------- | ---------------------------------------------------------------- |
| [`user_config`](roles/user_config/README.md)               | Per-user settings and environment setup.                         |
| [`system_config`](roles/system_config/README.md)           | System settings and environment setup.                           |
| [`install_cloud_clis`](roles/install_cloud_clis/README.md) | Cloud and Kubernetes CLIs for the connection user.               |
| [`openshift_local`](roles/openshift_local/README.md)       | Install or upgrade OpenShift Local (`crc`) for the target user.  |
| [`secureboot_signing`](roles/secureboot_signing/README.md) | Secure Boot kernel module signing (MOK, akmods, dkms) on Fedora. |

### Filter plugins

| Filter                                              | Summary                                                                                                   |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| [`to_gnome_clocks`](plugins/filter/gnome_clocks.py) | Build GNOME world-clock GVariant strings from location data (`branic.system_management.to_gnome_clocks`). |

<!--end collection content-->

## Using this collection

```bash
    ansible-galaxy collection install branic.system_management
```

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml` using the format:

```yaml
collections:
  - name: branic.system_management
```

To upgrade the collection to the latest available version, run the following command:

```bash
ansible-galaxy collection install branic.system_management --upgrade
```

You can also install a specific version of the collection, for example, if you need to downgrade when something is broken in the latest version (please report an issue in this repository). Use the following syntax where `X.Y.Z` can be any [available version](https://galaxy.ansible.com/branic/system_management):

```bash
ansible-galaxy collection install branic.system_management:==X.Y.Z
```

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Release notes

See the [changelog](https://github.com/branic/system_management/tree/main/CHANGELOG.rst).

## More information

- [Source repository](https://github.com/branic/system_management)
- [Issue tracker](https://github.com/branic/system_management/issues)
- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/devel/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/devel/dev_guide/index.html)
- [Ansible Collections Checklist](https://github.com/ansible-collections/overview/blob/main/collection_requirements.rst)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/devel/community/code_of_conduct.html)
- [The Bullhorn (the Ansible Contributor newsletter)](https://docs.ansible.com/ansible/devel/community/communication.html#the-bullhorn)
- [News for Maintainers](https://github.com/ansible-collections/news-for-maintainers)

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
