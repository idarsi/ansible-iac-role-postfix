# `configuration_present`

Converges managed `main.cf` settings, virtual alias/mailbox maps, and backup MX
recipient/transport maps when declared; builds map databases and checks the
configuration with `postfix check`. It ensures the vmail system account and
mailbox base and creates Maildirs for domain-scoped mailbox declarations. It
does not install Postfix or ensure the service is running. Changed map data is
reloaded only when the service is already running; listener changes notify a
restart handler.
