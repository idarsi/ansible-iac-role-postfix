# OpenSSF OSPS Baseline Level 1 self-assessment

> Self-assessment, not independent audit or certification. This is not a
> compliance claim.

- **Baseline:** OSPS 2026.02.19
- **Official source:** <https://baseline.openssf.org/versions/2026-02-19.html>
- **Project / repository URL:** <https://github.com/idarsi/ansible-iac-role-postfix>
- **Assessment scope:** This repository and its `tasks/shared` Git submodule; source and documentation, CI declarations and observed run results, and publicly/API-visible GitHub repository metadata. No deployed hosts or production systems.
- **Assessed commit:** `61f07cc5bdf6e32f511e0c4adea76c5fc6f88976` (`main`, merge commit; task checkout HEAD)
- **Local modifications:** Clean at start of assessment; no working-tree changes were evidence. The documentation edits from this assessment are not evidence for the assessed commit.
- **Assessment date:** 2026-10-31
- **Methods:** Read the pinned Level 1 catalog (`level-1-catalog-2026-02-19.md`) and shared interpretation; inspected tracked files, workflow, docs, submodule pointer/status, commit and tags; queried GitHub with authorized `gh` read-only commands for repository metadata, main branch protection/rulesets, releases, and Actions runs/jobs.
- **Visibility limitations:** The authenticated GitHub CLI returned public repo metadata, `main.protected: false`, and no repository rulesets; it did not establish effective organization policies, MFA, collaborator defaults, deletion safeguards, Actions secrets/effective token access, or runner isolation. A source inspection and green run do not prove those settings. No releases/tags were returned. No attempt was made to change settings.

Statuses: **Met** (sufficient current evidence establishes operation), **Unmet** (actual deficiency established), **Unverified** (evidence insufficient), **Not applicable** (official applicability condition unsatisfied and justified). Catalog requirement text and upstream recommendations are reproduced in the pinned catalog; Idarsi interpretation is in the accompanying `shared-interpretation.md`. This assessment distinguishes normative controls from recommendations.

## Requirement results

### OSPS-AC-01.01 — Multi-factor authentication

- **Applicability:** Applicable; control covers access to sensitive repository resources.
- **Status:** Unverified
- **Target area:** GitHub organization/repository settings
- **Implementation:** Effective MFA policy for relevant collaborators cannot be established from repository content or available CLI output.
- **Evidence:** `gh api repos/idarsi/ansible-iac-role-postfix` returned public repository metadata on 2026-10-31; no MFA setting evidence was available. Publicness does not prove MFA enforcement.
- **Necessary remediation:** Administrator review of effective organization/repository MFA policy.

### OSPS-AC-02.01 — Collaborator permissions

- **Applicability:** Applicable; repository may add collaborators.
- **Status:** Unverified
- **Target area:** GitHub organization/repository settings
- **Implementation:** Default/manual collaborator permission assignment was not observable.
- **Evidence:** Authenticated repository metadata query on 2026-10-31 did not expose collaborator defaults or effective organization policy.
- **Necessary remediation:** Administrator review of effective collaborator onboarding permissions.

### OSPS-AC-03.01 — Primary branch write protection

- **Applicability:** Applicable; `main` is primary branch.
- **Status:** Unverified
- **Target area:** GitHub organization/repository settings
- **Implementation:** GitHub branch API reported `protected: false` for `main` on 2026-10-31. Effective organization rulesets or alternate enforcement were not inspectable, so the API response alone does not establish whether direct commits are otherwise prevented.
- **Evidence:** `gh api repos/idarsi/ansible-iac-role-postfix/branches/main` returned `protected: false` and commit `61f07cc5bdf6e32f511e0c4adea76c5fc6f88976`. Organization rulesets and effective alternate enforcement were not inspectable.
- **Necessary remediation:** Administrator review effective branch/ruleset enforcement and ensure it prevents direct primary-branch commits if no equivalent protection is active.

### OSPS-AC-03.02 — Primary branch deletion protection

- **Applicability:** Applicable; `main` is primary branch.
- **Status:** Unverified
- **Target area:** GitHub organization/repository settings
- **Implementation:** Whether deleting `main` requires explicit intent was not established. `protected: false` is relevant but does not alone prove deletion behavior or exclude organization rulesets.
- **Evidence:** Branch API observation above; no effective deletion policy evidence available.
- **Necessary remediation:** Administrator review; require explicit confirmation or prohibit deletion.

### OSPS-BR-01.01 — Untrusted metadata validation

- **Applicability:** Applicable; PR branch metadata and workflow expressions are used.
- **Status:** Met
- **Target area:** Actions-runners-test infrastructure
- **Implementation:** Workflow matrix interpolation uses a fixed, workflow-defined scenario list; repository-controlled PR branch names are not interpolated into shell commands. `scripts/check_source_policy.py` and focused tests check workflow declaration policy.
- **Evidence:** `.github/workflows/tests.yml` at assessed commit has fixed `matrix.scenario` values and quotes the scenario in `molecule test -s`; `.github/workflows/tests.yml` and `scripts/check_source_policy.py`; successful source-check job in run `41216476534` on 2026-10-31. Assessment is limited to observed workflow/code paths.
- **Necessary remediation:** None evidenced for the inspected workflow. Continue reviewing newly introduced metadata-to-command paths.

### OSPS-BR-01.03 — Isolation of untrusted code snapshots

- **Applicability:** Applicable; workflow runs on `pull_request`.
- **Status:** Unverified
- **Target area:** Actions-runners-test infrastructure
- **Implementation:** Workflow declares `contents: read`, uses `ubuntu-latest`, and does not declare privileged triggers; however effective permissions, available secrets, runner isolation and internal-network reachability were not verified.
- **Evidence:** `.github/workflows/tests.yml` at assessed commit; successful PR run `41212418602` for `16cd60b7b4b2549647b91202559036ffdec9f0f8` on 2026-10-31 proves execution and result, not the absence of credentials/assets or all runner capabilities.
- **Necessary remediation:** CI administrator to verify effective token permissions, secrets exposure, hosted-runner isolation/cleanup and network reachability for untrusted PR code.

### OSPS-BR-03.01 — Encrypted official project channels

- **Applicability:** Applicable; project lists repository and documentation channels.
- **Status:** Met
- **Target area:** source-dependencies-distribution / documentation-maintenance
- **Implementation:** Official GitHub documentation links use HTTPS; repository remote uses SSH and shared-task submodule URL uses HTTPS.
- **Evidence:** README.md, CONTRIBUTING.md, TESTING.md, `.git/config`, `.gitmodules` at assessed commit; no plaintext official channel was identified in inspected files. This is a repository-content review, not a network/TLS audit of all linked services.
- **Necessary remediation:** None evidenced; periodically check new official channel URLs.

### OSPS-BR-03.02 — Authenticated distribution channel

- **Applicability:** Not applicable; GitHub API reported zero releases on 2026-10-31 and no release assets/channel were identified. This is conditional on released software assets.
- **Status:** Not applicable
- **Target area:** source-dependencies-distribution
- **Implementation:** No release distribution channel exists in the observed repository metadata.
- **Evidence:** `gh api repos/idarsi/ansible-iac-role-postfix/releases --jq 'length'` returned `0`; no Git tags were present at assessed commit.
- **Necessary remediation:** Reassess before publishing software through a distribution channel.

### OSPS-BR-07.01 — Prevent unencrypted sensitive data in VCS

- **Applicability:** Applicable.
- **Status:** Unverified
- **Target area:** source-dependencies-distribution
- **Implementation:** `.gitignore` and source checker are present, but no complete history scan or effective prevention control was performed. The passing source-check job is not a secret scanner.
- **Evidence:** `.gitignore`, `scripts/check_source_policy.py`, and run `41216476534` source-check job on 2026-10-31; none establishes prevention of unintentional secret storage across history.
- **Necessary remediation:** Verify current secret-scanning/pre-commit controls and review repository history without placing sensitive values in this report.

### OSPS-DO-01.01 — User guides for released functionality

- **Applicability:** Not applicable; conditional on a project release, and none was observed.
- **Status:** Not applicable
- **Target area:** documentation-maintenance
- **Implementation:** README and linked state/configuration guides document user functionality; absence of a release means the normative release condition is currently unsatisfied.
- **Evidence:** `README.md`, `docs/states/`, `docs/configuration-examples.md`; zero releases and no tags observed 2026-10-31.
- **Necessary remediation:** Keep guides current and reassess when making a release.

### OSPS-DO-02.01 — Defect reporting guide

- **Applicability:** Not applicable; conditional on a project release, and none was observed.
- **Status:** Not applicable
- **Target area:** documentation-maintenance
- **Implementation:** `CONTRIBUTING.md` explains contribution and testing procedures but does not explicitly document defect reporting; the normative release condition is not currently met.
- **Evidence:** `CONTRIBUTING.md`; GitHub release API returned zero on 2026-10-31.
- **Necessary remediation:** Add visible defect-reporting instructions before release.

### OSPS-GV-02.01 — Public discussions

- **Applicability:** Applicable; repository is active (latest main push 2026-10-31).
- **Status:** Met
- **Target area:** documentation-maintenance
- **Implementation:** Public GitHub repository provides issue and pull-request discussion channels.
- **Evidence:** Public repository URL and successful public PR run `41212418602` (2026-10-31) demonstrate an active public collaboration channel; GitHub repository metadata returned `visibility: public`.
- **Necessary remediation:** None evidenced.

### OSPS-GV-03.01 — Contribution process

- **Applicability:** Applicable; project active.
- **Status:** Met
- **Target area:** documentation-maintenance
- **Implementation:** Contribution process, blueprint change requirements, test guidance and scenarios are documented.
- **Evidence:** `CONTRIBUTING.md` and linked `TESTING.md` at assessed commit; current PR CI run `41212418602` on 2026-10-31.
- **Necessary remediation:** None evidenced.

### OSPS-LE-02.01 — Source license is open source/free

- **Applicability:** Applicable; project active.
- **Status:** Met
- **Target area:** source-dependencies-distribution
- **Implementation:** Source is identified as MIT-licensed.
- **Evidence:** `LICENSE` at assessed commit contains MIT License text; README identifies MIT. The source checker validates expected markers, not legal interpretation; MIT is an OSI-approved license.
- **Necessary remediation:** None evidenced.

### OSPS-LE-02.02 — Released assets license is open source/free

- **Applicability:** Not applicable; no released software assets or releases were observed.
- **Status:** Not applicable
- **Target area:** source-dependencies-distribution
- **Implementation:** Conditional release-asset control; no releases present.
- **Evidence:** GitHub releases API returned zero and no tags were present on 2026-10-31.
- **Necessary remediation:** Ensure any future released assets have an appropriate license.

### OSPS-LE-03.01 — Source license included in repository

- **Applicability:** Applicable; project active.
- **Status:** Met
- **Target area:** source-dependencies-distribution
- **Implementation:** License file is included at repository root.
- **Evidence:** `LICENSE` tracked at assessed commit.
- **Necessary remediation:** None evidenced.

### OSPS-LE-03.02 — License alongside released assets

- **Applicability:** Not applicable; no releases or release assets observed.
- **Status:** Not applicable
- **Target area:** source-dependencies-distribution
- **Implementation:** Conditional on released software assets.
- **Evidence:** GitHub release API returned zero on 2026-10-31.
- **Necessary remediation:** Include the applicable license with future release assets.

### OSPS-QA-01.01 — Public source repository

- **Applicability:** Applicable; project active.
- **Status:** Met
- **Target area:** GitHub organization/repository settings
- **Implementation:** GitHub API reports public visibility at the canonical static repository URL.
- **Evidence:** `gh api repos/idarsi/ansible-iac-role-postfix` returned `visibility: public`, URL `https://github.com/idarsi/ansible-iac-role-postfix` on 2026-10-31.
- **Necessary remediation:** None evidenced.

### OSPS-QA-01.02 — Public change history

- **Applicability:** Applicable.
- **Status:** Met
- **Target area:** GitHub organization/repository settings
- **Implementation:** Public Git repository history is available at the canonical repository; current `main` resolves to assessed commit.
- **Evidence:** `gh api repos/idarsi/ansible-iac-role-postfix/branches/main` returned commit `61f07cc5bdf6e32f511e0c4adea76c5fc6f88976`; public GitHub repository and commit history inspected 2026-10-31.
- **Necessary remediation:** None evidenced.

### OSPS-QA-02.01 — Direct dependency list

- **Applicability:** Applicable; test environment uses package-managed dependencies.
- **Status:** Met
- **Target area:** source-dependencies-distribution
- **Implementation:** Workflow and scenario requirement files identify/pin direct test dependencies; shared role tasks are pinned as a Git submodule.
- **Evidence:** `.github/workflows/tests.yml` pins ansible-core, ansible-lint, Molecule, plugin and PyYAML; `molecule/*/requirements.yml`; `.gitmodules` and gitlink at `tasks/shared` point to `d70d58eeb31390d36975fb8d9c11dfab88fadc95` on assessed commit. No application-language dependency manager applies to this Ansible role.
- **Necessary remediation:** None evidenced for current direct dependencies; keep pins current.

### OSPS-QA-04.01 — Project codebase list

- **Applicability:** Applicable; role consumes a separate shared-tasks repository.
- **Status:** Met
- **Target area:** source-dependencies-distribution / documentation-maintenance
- **Implementation:** Contribution/testing docs identify `ansible-iac-shared-tasks` as the role's shared-task submodule, its use, and the update boundary.
- **Evidence:** `CONTRIBUTING.md`, `TESTING.md`, `.gitmodules`, and pinned submodule gitlink at assessed commit. The local `git submodule status` marked `tasks/shared` uninitialized (`-d70d58e...`); CI's recursive checkout step succeeded in run `41216476534`, so the dependency is identified/pinned and available in CI, but not populated in this local checkout.
- **Necessary remediation:** None evidenced.

### OSPS-QA-05.01 — No generated executable artifacts

- **Applicability:** Applicable; repository active.
- **Status:** Met
- **Target area:** source-dependencies-distribution
- **Implementation:** Tracked file listing contains role source, text documentation/configuration and test files; no generated executable artifacts identified.
- **Evidence:** `git ls-files` / tree inspection at assessed commit; limited to tracked repository contents.
- **Necessary remediation:** None evidenced; keep generated artifacts out of VCS.

### OSPS-QA-05.02 — No unreviewable binary artifacts

- **Applicability:** Applicable; repository active.
- **Status:** Met
- **Target area:** source-dependencies-distribution
- **Implementation:** No unreviewable binary files identified in tracked tree.
- **Evidence:** `git ls-tree -r HEAD` and tracked-file inspection at assessed commit; no binary assets present.
- **Necessary remediation:** None evidenced.

### OSPS-VM-02.01 — Security contact

- **Applicability:** Applicable; project active.
- **Status:** Unmet
- **Target area:** documentation-maintenance
- **Implementation:** No `SECURITY.md` or equivalent security contact information was found in tracked files or inspected README/CONTRIBUTING documentation.
- **Evidence:** Tracked file listing and docs inspected at assessed commit; no security reporting contact identified.
- **Necessary remediation:** Add a security policy/contact with a monitored reporting channel.

## GitHub Actions run evidence

At assessment time, `gh run list` identified the latest run as **Tests** run
[41216476534](https://github.com/idarsi/ansible-iac-role-postfix/actions/runs/41216476534),
completed **success** for a `push` to `main` at assessed merge commit
`61f07cc5bdf6e32f511e0c4adea76c5fc6f88976` (created 2026-10-31 15:46:53Z).
All listed jobs succeeded: Ansible Lint; source checks; and Molecule matrix
scenarios `default`, `rocky10`, `ubi9`, `ubi10`, `validation`, `lifecycle`,
`lmdb`, and `mail-flow`. This is run evidence at the assessed ref, not evidence
of branch-protection/required-check enforcement, private settings, or runtime
security beyond the job activity/result.

The associated PR run
[41212418602](https://github.com/idarsi/ansible-iac-role-postfix/actions/runs/41212418602)
also completed successfully for `pull_request` from
`update/postfix-osps-assessment` at `16cd60b7b4b2549647b91202559036ffdec9f0f8`
on 2026-10-31. Earlier PR runs included failures, including run `41209164145`
for `1cfbd8abe4da1bd1a664f7b48e51b0248e51a0f7` (2026-10-31 14:13:54Z).
Those failures are historical and do not change the successful status of the
latest assessed-main run; neither current success erases the earlier failures.

The workflow's source-check job executes `scripts/check_source_policy.py` and
its standard-library tests. It inspects selected source declarations and
artifacts only; it is not a complete OSPS audit, secret scan, test of GitHub
settings, or verification of effective token permissions or runner isolation.
Successful Molecule jobs provide role behavior evidence only for the listed
scenarios/images; UBI is not subscribed RHEL evidence. README/TESTING documents
that RHEL 9/10 are declared but not tested on subscribed RHEL hosts.

## Outstanding external settings and actions

| Setting/action | Related requirement(s) | Evidence/limitation | Owner or required access | Status/action |
|---|---|---|---|---|
| Verify MFA and collaborator default permissions | AC-01.01, AC-02.01 | Effective policies unavailable | GitHub organization administrator | Unverified; inspect effective policies |
| Verify primary branch protections/rulesets and deletion safeguards | AC-03.01, AC-03.02 | Branch API reports `protected: false`; org rulesets/effective alternate enforcement not inspectable | GitHub repository/organization administrator | AC-03.01 Unverified; verify effective enforcement and remediate if needed; AC-03.02 Unverified |
| Verify Actions token/secret permissions, runner isolation, cleanup and network access for untrusted PRs | BR-01.03 | Workflow declarations and successful PR run do not prove effective execution boundary | CI administrator | Unverified; inspect effective configuration and runner boundary |
| Verify secret-detection prevention and repository history | BR-07.01 | Source checks are not secret scanning; no history-wide scan | Repository/CI administrator | Unverified; review configured prevention and history |
| Add a security reporting contact | VM-02.01 | No contact found in tracked docs | Project maintainer | Unmet; add monitored contact |

## Assessment conclusion

- **Level 1 result:** Not established; applicable controls remain Unmet or Unverified.
- **Unmet controls:** OSPS-VM-02.01.
- **Unverified controls:** OSPS-AC-01.01, OSPS-AC-02.01, OSPS-AC-03.01, OSPS-AC-03.02, OSPS-BR-01.03, OSPS-BR-07.01.
- **Not applicable:** OSPS-BR-03.02, OSPS-DO-01.01, OSPS-DO-02.01, OSPS-LE-02.02, OSPS-LE-03.02; each is release-conditioned and no release/assets were observed.
- **Scope caveat:** This assessment does not determine deployed-server hardening and does not replace an Ansible implementation security review. Green CI is evidence only for the recorded jobs and commit, not a baseline compliance claim.
