# Testing

This role uses Molecule with the Podman driver for integration testing. The
current scenarios cover the supported RHEL-compatible base images used during
development.

## Automated test matrix

| Platform/image | Ansible or application versions | Molecule scenarios | Main coverage |
|---|---|---|---|
| Rocky Linux 9 UBI | Postfix from image repositories | `default`, `validation`, `lifecycle`, `lmdb`, `mail-flow` | Installation, validation, lifecycle, idempotence, map backends, and SMTP delivery |
| Rocky Linux 10 UBI | Postfix from image repositories | `rocky10` | Installation and configuration compatibility |

This is the tested subset. RHEL 9 and 10 are supported but are not currently
executed by the Molecule matrix.

## Scenario coverage

- `molecule/default` runs the full Postfix installation and configuration flow
  on Rocky Linux 9 UBI. It verifies:
  - package installation and service startup
  - virtual mailbox and alias domains
  - explicit virtual mailbox rows
  - backup MX relay domains, recipient maps, and transport maps
  - Postfix map lookups and `postfix check`
  - Maildir directories created through the shared filesystem tasks
- `molecule/rocky10` runs the same coverage on Rocky Linux 10 UBI.
- `molecule/validation` validates a valid blueprint and verifies that domain
  class overlap, incomplete backup MX records, duplicates, malformed records,
  unsafe domains, case-insensitive protected parameters, unsupported backends,
  case-insensitive record/domain identity checks, whitespace-protected keys,
  and control-character injection fail with explicit messages before any
  Postfix package or service work is attempted. The valid blueprint also
  covers successful backup MX validation.
- `molecule/lifecycle` exercises targeted alias/mailbox states and the
  started/stopped/restarted/absent/uninstall service lifecycle.
- `molecule/lmdb` repeats the default scenario with LMDB map databases.
- `molecule/mail-flow` uses SMTP against the running Postfix service to verify
  virtual mailbox delivery into Maildir `new/`, virtual alias delivery to the
  target mailbox, unknown-recipient rejection, and backup-MX acceptance. The
  checks use `ncat` as an interactive SMTP client: each transaction reads and
  validates the greeting, EHLO, MAIL FROM, RCPT TO, DATA, and final response
  independently using CRLF line endings. Each run gets a controller-generated
  token; mailbox checks require both that run's Message-ID and body, so an old
  message cannot satisfy the assertion. The backup-MX assertion checks
  Postfix's SMTP queue response rather than requiring the queue entry to remain
  present while delivery retries run.

Non-validation states require the `tasks/shared` Git submodule. A missing
submodule produces a preflight error; validation-only runs remain host-state
free.

## Running tests

Run all scenarios from the role directory:

```bash
molecule test
```

Run an individual scenario:

```bash
molecule test -s default
molecule test -s rocky10
molecule test -s validation
molecule test -s lifecycle
molecule test -s lmdb
molecule test -s mail-flow
```

Run only syntax checks while editing task or scenario structure:

```bash
molecule syntax -s default
molecule syntax -s rocky10
molecule syntax -s validation
molecule syntax -s lifecycle
molecule syntax -s lmdb
molecule syntax -s mail-flow
```

Lint the mail-flow playbooks directly (the repository-wide Ansible Lint
configuration excludes `molecule/`):

```bash
ansible-lint --profile production molecule/mail-flow/verify.yml molecule/mail-flow/converge.yml
```

The scenarios use the `ansible.posix` and `containers.podman` collections for
test infrastructure. The role itself uses `ansible.builtin.*` modules and its
`tasks/shared` Git submodule.

## GitHub Actions

The repository workflow at `.github/workflows/tests.yml` runs on pull requests,
pushes to `main`, and manual dispatches. It performs a production-profile
`ansible-lint` check and runs every Molecule scenario on an Ubuntu GitHub runner
with Podman. The workflow checks out `tasks/shared` recursively so the role is
tested with its pinned shared-task dependency.

Run the production-profile lint check locally before running the Molecule
scenarios:

```bash
ANSIBLE_ROLES_PATH=.. ansible-lint --profile production
```

Molecule's current releases do not provide Ansible Lint as a built-in scenario
phase, so lint is a separate static-analysis gate in the same GitHub Actions
workflow. The repository's `.ansible-lint` file keeps the profile and shared
task exclusions in version control.
