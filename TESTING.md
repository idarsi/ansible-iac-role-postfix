# Testing

The `source-checks` job runs `scripts/check_source_policy.py` and the focused
`unittest` suite. The checker parses workflow YAML with pinned PyYAML 6.0.2,
checks top-level and any job-level permission declarations independently,
rejects the sensitive `pull_request_target` and `workflow_run` triggers, and
checks expected project markers in documentation and MIT license text. Fixtures
cover a job-level write override, a sensitive trigger, and broad top-level
permissions. These are source-declaration checks only: they do not calculate
effective permissions from GitHub administration settings, inspect token use,
validate the legal status of the license, assess documentation quality, or
verify runner/secret isolation. The tests use Python's standard-library
`unittest`; only the checker requires the pinned YAML parser.

This role uses Molecule with the Podman driver for integration testing. Rocky
Linux images are used for local/CI coverage; they do not constitute RHEL
testing.

## Automated test matrix

| Platform/image | Ansible or application versions | Molecule scenarios | Main coverage |
|---|---|---|---|
| Rocky Linux 9 container | Postfix from image repositories | `default`, `validation`, `lifecycle`, `lmdb`, `mail-flow` | Installation, validation, lifecycle, map backends, and SMTP delivery |
| Rocky Linux 10 container | Postfix from image repositories | `rocky10` | Installation and configuration compatibility |
| Red Hat UBI 9 init container | Postfix from UBI repositories | `ubi9` | Installation and configuration compatibility |
| Red Hat UBI 10 init container | Postfix from UBI repositories | `ubi10` | Installation and configuration compatibility |

RHEL 9 and 10 are declared supported by the role, but are not tested on
subscribed RHEL hosts. The UBI scenarios use Red Hat's freely redistributable
UBI container images and UBI repositories. They verify the role against UBI's
package and systemd environment only; they do not verify full RHEL subscription,
entitlement, or repository behavior and are not a substitute for an authenticated
RHEL 9/10 VM matrix.

## Scenario coverage

- `molecule/default` runs the full Postfix installation and configuration flow
  on Rocky Linux 9 UBI. It verifies:
  - package installation and service startup
  - virtual mailbox and alias domains
  - explicit virtual mailbox rows
  - backup MX relay domains, recipient maps, and transport maps
  - Postfix map lookups and `postfix check`
  - Maildir directories created through the shared filesystem tasks
- `molecule/rocky10` runs the same coverage on the Rocky Linux 10 init image.
- `molecule/ubi9` and `molecule/ubi10` run the installation and configuration
  checks against genuine Red Hat UBI 9 and UBI 10 init images respectively.
- `molecule/validation` validates a valid blueprint and verifies that domain
  class overlap, incomplete backup MX records, duplicates, malformed records,
  unsafe domains, case-insensitive protected parameters, unsupported backends,
  case-insensitive record/domain identity checks, whitespace-protected keys,
  assignment-syntax extra parameter keys,
  TLS configuration overrides, and control-character injection fail with
  explicit messages before any Postfix package or service work is attempted.
  Unsupported states and invalid configuration non-mutation are checked too.
  The valid blueprint also covers successful backup MX validation.
- `molecule/lifecycle` exercises targeted alias/mailbox states and the
  started/stopped/restarted/absent/uninstall service lifecycle, repeated
  started/stopped transitions, configuration check mode, omitted-state
  recovery, and preservation of mailbox data through uninstall. It also checks
  mailbox symlink removal refusal and isolation from caller-provided
  `iac_fs_files` records, mailbox creation/removal, and unsafe path rejection.
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
molecule test -s ubi9
molecule test -s ubi10
molecule test -s validation
molecule test -s lifecycle
molecule test -s lmdb
molecule test -s mail-flow
```

Run only syntax checks while editing task or scenario structure:

```bash
molecule syntax -s default
molecule syntax -s rocky10
molecule syntax -s ubi9
molecule syntax -s ubi10
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

The UBI 9 and UBI 10 init images use fully qualified, immutable Docker Hub
digest references (`docker.io/redhat/ubi9-init` and
`docker.io/redhat/ubi10-init`) to avoid Podman's short-name resolution and keep
scenario base images reproducible; update the digests intentionally when
refreshing the images. The corresponding UBI AppStream repositories publish
the `postfix` RPM. The init images use systemd for service management. The scenarios use the
`ansible.posix` and `containers.podman` collections for test infrastructure.
The role itself uses `ansible.builtin.*` modules and its `tasks/shared` Git
submodule.

## GitHub Actions

The repository workflow at `.github/workflows/tests.yml` runs on pull requests,
pushes to `main`, and manual dispatches. It performs a production-profile
`ansible-lint` check and runs every Molecule scenario on an Ubuntu GitHub runner
with Podman. Its matrix includes `ubi9` and `ubi10`. The workflow checks out
`tasks/shared` recursively so the role is tested with its pinned shared-task
dependency.

Run the production-profile lint check locally before running the Molecule
scenarios:

```bash
ANSIBLE_ROLES_PATH=.. ansible-lint --profile production
```

Molecule's current releases do not provide Ansible Lint as a built-in scenario
phase, so lint is a separate static-analysis gate in the same GitHub Actions
workflow. The repository's `.ansible-lint` file keeps the profile and shared
task exclusions in version control.
