# `virtual_mailbox_absent`

Removes only the explicitly supplied `postfix_virtual_mailbox_targets` map
entries and their corresponding Maildir directories, then rebuilds map
databases. At least one target is required. Before removal it checks the base
and target paths against traversal and symlink escapes; unsafe paths fail
rather than being removed. It does not remove the vmail account/base or
unrelated mail data, converge the full blueprint, or restart/reload Postfix.
