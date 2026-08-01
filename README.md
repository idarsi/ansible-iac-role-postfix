ANSIBLE-IAC-ROLE-POSTFIX
========================
**COPYRIGHT** 2026 ^(ida|arsi)$ collective  
**LICENSE** MIT License [LICENSE](LICENSE)  
**AUTHORS**
- Arsi Atomi <arsi@atomi.sh>  
- Arsi Atomi <arsi.atomi@valtori.fi>  

Overview
========

This Ansible role installs and configures Postfix on RHEL-compatible systems.
It supports virtual alias domains so one Postfix instance can receive mail for
multiple domains and route addresses to local users or other destinations.
It also supports virtual mailbox domains backed by Maildir directories under
`/var/vmail/<domain>/<user>/`.

These operations are supported:

Operation                                  | State                 |
-------------------------------------------|-----------------------|
Installing, configuring, and starting Postfix | install            |
Stopping and removing Postfix package      | uninstall             |
Installing and configuring Postfix         | present               |
Stopping and removing Postfix package      | absent                |
Updating Postfix configuration files       | configuration_present |
Ensuring virtual domain targets            | virtual_domain_present|
Removing virtual domain targets            | virtual_domain_absent |
Ensuring virtual alias targets             | virtual_alias_present |
Removing virtual alias targets             | virtual_alias_absent  |
Ensuring virtual mailbox targets           | virtual_mailbox_present |
Removing virtual mailbox targets           | virtual_mailbox_absent |
Starting Postfix                           | started               |
Stopping Postfix                           | stopped               |
Restarting Postfix                         | restarted             |

Requirements
------------

- Operating system
  - Red Hat Enterprise Linux 9
  - Red Hat Enterprise Linux 10
  - Rocky Linux 9
  - Rocky Linux 10

- Other components
  - Ansible 2.15 or higher

Configuration
-------------

Role data is read from `iac_blueprint.postfix`.

This role manages:

- selected `main.cf` settings through `postfix.configuration`
- additional `main.cf` lines through `postfix.configuration.extra_parameters`
- virtual alias maps through `virtual_domains[].aliases` and `virtual_aliases`
- virtual mailbox maps through `virtual_domains[].mailboxes` and `virtual_mailboxes`
- Maildir directory creation under `{{ postfix_virtual_mailbox_base }}`

This role does not currently manage:

- `master.cf`
- SASL authentication setup
- TLS certificate provisioning
- milters, header checks, transport maps, or other non-virtual map families

See [docs/configuration-examples.md](docs/configuration-examples.md) for fuller inventory examples.

Example:

```yaml
iac_blueprint:
  postfix:
    configuration:
      myhostname: "mail.example.com"
      mydomain: "example.com"
      inet_interfaces: "all"
      inet_protocols: "all"
      extra_parameters:
        smtpd_banner: "$myhostname ESMTP"
    virtual_domains:
      - name: "example.com"
        mailboxes:
          - user: "info"
          - user: "sales"
        aliases:
          - source: "info@example.com"
            destination: "info@example.com"
          - source: "@example.com"
            destination: "sales@example.com"
      - name: "example.net"
        mailboxes:
          - user: "admin"
        aliases:
          - source: "admin@example.net"
            destination: "admin@example.net"
```

Virtual Domains
---------------

Virtual domains are configured with `virtual_alias_domains` and
`virtual_alias_maps`. The role writes `/etc/postfix/virtual` and runs `postmap`
when the map changes. Domain-scoped aliases are declared under
`virtual_domains[].aliases`.

The role also supports top-level `virtual_aliases` for alias entries that are
not tied to a single `virtual_domains[]` item.

Use `source: "@domain.example"` for a catch-all route. Destinations may be local
users or valid Postfix alias destinations.

Virtual Mailboxes
-----------------

Define mailbox users under each domain with `virtual_domains[].mailboxes`.
The role creates:

- system group `vmail` (GID `5000`)
- system user `vmail` (UID `5000`, shell `/sbin/nologin`)
- mailbox base directory `/var/vmail`
- Maildir paths:
  - `/var/vmail/<domain>/<user>/`
  - `/var/vmail/<domain>/<user>/new`
  - `/var/vmail/<domain>/<user>/cur`
  - `/var/vmail/<domain>/<user>/tmp`

The role writes `virtual_mailbox_domains`, `virtual_mailbox_maps`,
`virtual_mailbox_base`, `virtual_uid_maps`, and `virtual_gid_maps` to
`main.cf`, writes `/etc/postfix/vmailbox`, and runs `postmap` for the mailbox
map.

The role also supports explicit top-level `virtual_mailboxes` entries with
`address` and `path` fields when you want to define mailbox map rows directly.

Substates for Targeted Changes
------------------------------

Use these keys for resource-scoped substate runs:

- `iac_blueprint.postfix.virtual_domain_targets`:
  - entries like `{ name: "example.com", aliases: [...], mailboxes: [...] }`
- `iac_blueprint.postfix.virtual_alias_targets`:
  - entries like `{ source: "user@example.com", destination: "target" }`
- `iac_blueprint.postfix.virtual_mailbox_targets`:
  - entries like `{ domain: "example.com", user: "user1" }`

This allows running one substate at a time to add/remove only selected
domains, aliases, or mailbox users.

Examples
--------

- Minimal inventory example: [docs/inventory-example.yml](docs/inventory-example.yml)
- Playbook example: [docs/playbook-example.yml](docs/playbook-example.yml)
- Extended configuration examples: [docs/configuration-examples.md](docs/configuration-examples.md)

Code Quality
------------

This project follows the Engine Ansible role coding standard.
