# `virtual_alias_absent`

Removes only the explicitly supplied `postfix_virtual_alias_targets` sources
from the virtual alias source map, rebuilds map databases, and logs the
operation. At least one target is required. It does not remove other aliases,
converge the full blueprint, or restart/reload the service.
