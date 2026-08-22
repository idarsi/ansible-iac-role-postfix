# Postfix Configuration Examples

This document collects fuller inventory examples for the Postfix role.

The role's task-report logging and Maildir directory operations use the shared
task library under `tasks/shared`.

## Main Configuration With Extra Parameters

Use `iac_blueprint.postfix.configuration` for the main supported `main.cf`
settings, and `extra_parameters` for additional plain `key = value` lines.

```yaml
iac_blueprint:
  postfix:
    configuration:
      myhostname: "mail.example.com"
      mydomain: "example.com"
      myorigin: "$mydomain"
      inet_interfaces: "all"
      inet_protocols: "all"
      mydestination:
        - "$myhostname"
        - "localhost.$mydomain"
        - "localhost"
      mynetworks:
        - "127.0.0.0/8"
        - "[::1]/128"
      smtpd_recipient_restrictions:
        - "permit_mynetworks"
        - "reject_unauth_destination"
      extra_parameters:
        smtpd_banner: "$myhostname ESMTP"
        relayhost: "[smtp.example.net]:587"
        smtp_use_tls: "yes"
```

## Domain-Scoped Virtual Aliases And Mailboxes

This is the primary model supported by the role.

```yaml
iac_blueprint:
  postfix:
    configuration:
      myhostname: "mail.example.com"
      mydomain: "example.com"
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
```

## Top-Level Virtual Aliases

Use `virtual_aliases` when an alias row does not naturally belong under a
single domain entry.

```yaml
iac_blueprint:
  postfix:
    virtual_aliases:
      - source: "postmaster@example.com"
        destination: "root"
      - source: "abuse@example.com"
        destination: "security-team@example.net"
```

## Explicit Virtual Mailbox Map Rows

Use `virtual_mailboxes` when you want to define `/etc/postfix/vmailbox`
entries directly with exact mailbox paths.

```yaml
iac_blueprint:
  postfix:
    virtual_mailboxes:
      - address: "archive@example.com"
        path: "example.com/archive/"
      - address: "support@example.net"
        path: "example.net/support/"
```

## Backup MX Domains

Backup MX domains accept mail for the explicit recipient list, queue it locally,
and relay it to the primary mail host after connectivity returns.

```yaml
iac_blueprint:
  postfix:
    backup_mx_domains:
      - name: "example.org"
        primary_mx: "mail.example.org"
        recipients:
          - "info@example.org"
          - "sales@example.org"
```

The role generates `relay_domains`, `relay_recipient_maps`, and
`transport_maps`. `primary_mx` is a hostname only; the generated transport
uses `smtp:[primary_mx]` so delivery goes directly to that host.

## Targeted Substate Examples

Use the targeted keys under `iac_blueprint.postfix` when running a narrower
state such as `virtual_alias_present` or `virtual_mailbox_absent`.

### Add one alias target

```yaml
iac_blueprint:
  postfix:
    virtual_alias_targets:
      - source: "ops@example.com"
        destination: "root"
```

### Remove one mailbox target

```yaml
iac_blueprint:
  postfix:
    virtual_mailbox_targets:
      - domain: "example.com"
        user: "olduser"
```
