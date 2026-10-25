# `absent`

Stops and disables Postfix when its package is installed, then removes the
package. It does not remove configuration files, generated maps, the `vmail`
account or mailbox base, or mail data. Use `virtual_mailbox_absent` for
explicitly targeted Maildirs; that state also updates its map.
