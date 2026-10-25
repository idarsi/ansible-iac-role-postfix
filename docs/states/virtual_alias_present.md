# `virtual_alias_present`

Adds or replaces the explicitly supplied `postfix_virtual_alias_targets`
entries in the virtual alias source map, rebuilds map databases, and logs the
operation. At least one target is required. It does not derive targets from
the blueprint's domain records, converge all configuration, or restart/reload
the service.
