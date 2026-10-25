# `validate`

Validates the complete `iac_blueprint.postfix` input, including domain classes,
overlaps, alias/mailbox records, and required backup MX fields. It performs no
host-runtime checks and makes no host changes. Non-validate states also run
this preflight before their state-specific work.
