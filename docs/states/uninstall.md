# `uninstall`

Runs the `absent` workflow: stops and disables Postfix, then removes its
package. This is not a full inverse of configuration setup: it leaves
configuration files, maps, virtual-mailbox identities/base and mailbox data
in place. It does not remove unrelated files or data.
