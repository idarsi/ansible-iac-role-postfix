# `virtual_mailbox_present`

Ensures the vmail system group/user and mailbox base, adds or replaces the
explicit `postfix_virtual_mailbox_targets` map entries, creates their Maildir
directories, and rebuilds map databases. Each target requires a domain and
user, and at least one target is required. It does not install Postfix or
converge unrelated configuration, and does not restart/reload the service.
