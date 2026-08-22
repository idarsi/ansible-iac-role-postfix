# Testing

This role uses Molecule with the Podman driver for integration testing. The
current scenarios cover the supported RHEL-compatible base images used during
development.

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
  class overlap and incomplete backup MX records fail before any Postfix
  package or service work is attempted.
- `molecule/lifecycle` exercises targeted alias/mailbox states and the
  started/stopped/restarted/absent/uninstall service lifecycle.
- `molecule/lmdb` repeats the default scenario with LMDB map databases.

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
```

Run only syntax checks while editing task or scenario structure:

```bash
molecule syntax -s default
molecule syntax -s rocky10
molecule syntax -s validation
molecule syntax -s lifecycle
molecule syntax -s lmdb
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
