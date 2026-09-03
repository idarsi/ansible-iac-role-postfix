# Contributing

## Blueprint changes

Every new or changed `iac_blueprint.postfix` field must be handled in all
relevant places:

- Add or update the hierarchical preflight validation under `tasks/validate/`.
- Add or update a valid inventory example when the inventory shape is
  user-visible.
- Add at least one Molecule assertion for invalid values or combinations when
  the change introduces validation rules.
- Update `README.md`, `docs/inventory-example.yml`, and
  `docs/configuration-examples.md` when the inventory structure or supported
  state surface changes.

Keep blueprint validation separate from host-state checks. Domain-class
membership, required backup MX fields, allowed values, cross-record
consistency, and impossible combinations belong in the configuration
validation. Checks that depend on the current host, installed packages,
services, files, or Postfix map databases remain in the state-specific tasks.

`absent` and `uninstall` must not remove the virtual mailbox base or unmanaged
mail data. Targeted mailbox removal must retain absolute-path and traversal
guardrails.

The three Postfix domain classes are mutually exclusive:

- `virtual_alias_domains`
- `virtual_mailbox_domains`
- `backup_mx_domains`

Backup MX records must contain an explicit `name`, `primary_mx`, and non-empty
`recipients` list. Do not weaken this requirement without adding a test that
proves the resulting recipient acceptance is safe.

## Shared tasks

The role consumes `ansible-iac-shared-tasks` through the `tasks/shared` Git
submodule. Keep service-specific preparation in Postfix task files and call
the shared task only through a small wrapper when the shared contract applies.

Current shared-task use covers:

- task-report logging through `tasks/log_write.yml`
- Maildir directory creation and removal through the filesystem wrappers

Do not add generic `cron`, `git`, or bind-mount inventory fields to Postfix
unless Postfix gains a clear responsibility for them. Shared-task changes
belong in the shared-tasks repository; update the submodule pointer in this
role separately when a new shared commit is required.

## Tests

Run the default scenario after changes that affect normal installation,
configuration, map generation, or Maildir handling:

```bash
molecule test -s default
```

Run the Rocky Linux 10 scenario when changing behavior that should work on
both supported Rocky Linux releases:

```bash
molecule test -s rocky10
```

Run the validation scenario when changing blueprint validation or state
dispatch behavior:

```bash
molecule test -s validation
```

Run the focused lifecycle and LMDB scenarios when changing state dispatch,
service handling, or map backend behavior:

```bash
molecule test -s lifecycle
molecule test -s lmdb
```

Run syntax checks while working on task or scenario structure:

```bash
molecule syntax -s default
molecule syntax -s rocky10
molecule syntax -s validation
molecule syntax -s lifecycle
molecule syntax -s lmdb
```

The default scenario should cover successful input and the resulting host
state. When adding validation rules, add a focused scenario or converge task
that demonstrates both accepted input and the expected failure message.

Before submitting changes, run the relevant Molecule scenarios and an Ansible
syntax check from the role directory:

```bash
ansible-playbook --syntax-check \
  -i 'mail_servers,' \
  docs/playbook-example.yml
```

See [TESTING.md](TESTING.md) for the current scenario coverage and execution
requirements.
