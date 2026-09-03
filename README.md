ANSIBLE-IAC-ROLE-POSTFIX
========================
**COPYRIGHT** 2026 ^(ida|arsi)$ collective  
**LICENSE** MIT License [LICENSE](LICENSE)  
**AUTHORS**
- Arsi Atomi <arsi@atomi.sh>  

Overview
========

This Ansible role provides a declarative way to deploy and manage Postfix mail
transfer agents on RHEL-compatible systems. It supports one Postfix instance
serving multiple domain classes: virtual alias domains, virtual mailbox domains,
and backup MX domains for temporarily queueing mail while a primary mail server
is unavailable.

Its development goal is to make multi-domain mail reception and delivery
behavior possible to roll out and maintain with as little manual work as
possible. The role is also intended to continuously verify that the deployed
Postfix configuration, recipient maps, transport maps, and Maildir structure
remain aligned with the desired blueprint.

The role uses the `iac_blueprint` model to keep the desired mail service state
in one structured inventory while Ansible handles the host-specific
implementation.

Virtual mailbox domains use Maildir directories under
`/var/vmail/<domain>/<user>/`. Backup MX domains require an explicit recipient
list, so the server can queue valid recipients without accepting arbitrary
addresses.

These operations are supported:

Operation                                  | State                 |
-------------------------------------------|-----------------------|
Installing, configuring, and starting Postfix | install            |
Stopping and removing Postfix package      | uninstall             |
Installing and configuring Postfix         | present               |
Stopping and removing Postfix package      | absent                |
Updating Postfix configuration files       | configuration_present |
Validating the Postfix blueprint            | validate               |
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

Blueprint Validation
--------------------

All supported states validate the complete `iac_blueprint.postfix` before
running state-specific work. Validation checks the domain class structure,
duplicate and overlapping domains, alias and mailbox records, and required
backup MX fields. Run validation without changing the host with:

```yaml
- hosts: mail_servers
  roles:
    - role: ansible-iac-role-postfix
      state: validate
```

`postfix_maps_type` is the preferred map backend variable (`auto`, `hash`, or
`lmdb`). The legacy `postfix_virtual_alias_maps_type` name remains accepted.
`extra_parameters` cannot override settings managed by this role or
safety-critical recipient and relay restrictions.

This role manages:

- selected `main.cf` settings through `postfix.configuration`
- additional `main.cf` lines through `postfix.configuration.extra_parameters`
- virtual alias maps through `virtual_alias_domains[].aliases`,
  `virtual_mailbox_domains[].aliases`, and `virtual_aliases`
- virtual mailbox maps through `virtual_mailbox_domains[].mailboxes` and
  `virtual_mailboxes`
- backup MX delivery through `backup_mx_domains`, including recipient and
  transport maps
- Maildir directory creation under `{{ postfix_virtual_mailbox_base }}`

This role does not currently manage:

- `master.cf`
- SASL authentication setup
- TLS certificate provisioning
- milters, header checks, or other non-virtual map families

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
    virtual_mailbox_domains:
      - name: "example.com"
        mailboxes:
          - user: "info"
          - user: "sales"
        aliases:
          - source: "info@example.com"
            destination: "info@example.com"
          - source: "@example.com"
            destination: "sales@example.com"
    virtual_alias_domains:
      - name: "aliases.example.net"
        aliases:
          - source: "admin@aliases.example.net"
            destination: "admin@example.com"
    backup_mx_domains:
      - name: "example.org"
        primary_mx: "mail.example.org"
        recipients:
          - "info@example.org"
          - "sales@example.org"
    virtual_mailboxes:
      - address: "archive@example.com"
        path: "example.com/archive/"
```

Virtual Alias Domains
---------------------

Virtual alias domains are configured with `virtual_alias_domains` and
`virtual_alias_maps`. Domain-scoped aliases are declared under
`virtual_alias_domains[].aliases`.

The role also supports top-level `virtual_aliases` for alias entries that are
not tied to a single domain item.

Use `source: "@domain.example"` for a catch-all route. Destinations may be local
users or valid Postfix alias destinations.

Virtual Mailboxes
-----------------

Define mailbox users under each domain with `virtual_mailbox_domains[].mailboxes`.
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
These entries enable the virtual mailbox map even when no domain-scoped
mailbox records exist.

`virtual_mailbox_absent` removes only explicitly listed mailbox targets and
their Maildir directories. `absent` and `uninstall` stop and remove the
Postfix package; they do not remove the configured mailbox base or unrelated
mail data. Mailbox removal rejects unsafe base paths, broad bases such as
`/var`, `/home`, and `/opt`, and path traversal.

Backup MX Domains
-----------------

Define a backup MX domain with a primary mail host and an explicit recipient
list. The role writes `relay_domains`, `relay_recipient_maps`, and
`transport_maps`. Accepted mail is queued by Postfix and delivered to
`primary_mx` after that host becomes reachable again.

Every backup domain must have an explicit `recipients` list. This prevents the
backup server from accepting arbitrary recipients and becoming a backscatter
source or an open relay.

The three domain classes are mutually exclusive: a domain must not appear in
`virtual_alias_domains`, `virtual_mailbox_domains`, and `backup_mx_domains` at
the same time.

Shared Task Helpers
-------------------

The role includes the shared task library under `tasks/shared`. Postfix uses
the shared wrappers for task-report logging and for creating or removing the
Maildir directory tree. The directory records are derived automatically from
`virtual_mailbox_domains[].mailboxes`:

```yaml
iac_blueprint:
  postfix:
    virtual_mailbox_domains:
      - name: "example.com"
        mailboxes:
          - user: "info"
```

This produces the following shared filesystem records for the `vmail` user and
group:

```text
/var/vmail/example.com/info/
/var/vmail/example.com/info/new/
/var/vmail/example.com/info/cur/
/var/vmail/example.com/info/tmp/
```

The exact shared filesystem task behavior is documented in
[`tasks/shared/README.md`](tasks/shared/README.md). Generic `directories`,
`files`, `cron`, `git`, and `binds` inventory fields are intentionally not
exposed by this role because they are outside Postfix's responsibility.

Substates for Targeted Changes
------------------------------

Use these keys for resource-scoped substate runs:

- `iac_blueprint.postfix.virtual_alias_targets`:
  - entries like `{ source: "user@example.com", destination: "target" }`
- `iac_blueprint.postfix.virtual_mailbox_targets`:
  - entries like `{ domain: "example.com", user: "user1" }`

This allows running one substate at a time to add/remove selected aliases or
mailbox users. Domain class changes are applied with
`configuration_present`.

Examples
--------

- Minimal inventory example: [docs/inventory-example.yml](docs/inventory-example.yml)
- Playbook example: [docs/playbook-example.yml](docs/playbook-example.yml)
- Extended configuration examples: [docs/configuration-examples.md](docs/configuration-examples.md)
- Molecule testing guide: [TESTING.md](TESTING.md)
- Contribution guide: [CONTRIBUTING.md](CONTRIBUTING.md)

Code Quality
------------

This project follows the Engine Ansible role coding standard.

Repository Checkout
-------------------

The shared task library is included as a Git submodule under `tasks/shared`.
Clone the role with submodules:

```bash
git clone --recurse-submodules https://github.com/idarsi/ansible-iac-role-postfix.git
```

If the role was already cloned without submodules, initialize them with:

```bash
git submodule update --init --recursive
```
