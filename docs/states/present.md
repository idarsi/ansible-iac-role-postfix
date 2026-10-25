# `present`

Installs the Postfix package, reloads systemd's manager, and converges the
role-managed configuration and maps, including declared Maildir directories.
It does not ensure the service is started or enabled. Configuration
convergence ensures the `vmail` system user/group and configured mailbox base;
it does not provision TLS certificates, SASL, `master.cf`, or other
unmanaged Postfix configuration.
