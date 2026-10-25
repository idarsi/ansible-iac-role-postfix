# `install`

Runs the `present` workflow and then ensures the Postfix service is started and
enabled at boot. The `present` workflow installs the package and converges
configuration, maps, and declared Maildir directories. It does not provision
TLS certificates, SASL, `master.cf`, or unrelated map families.
