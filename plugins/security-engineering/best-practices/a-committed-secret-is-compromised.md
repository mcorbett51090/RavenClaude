# Treat a committed secret as compromised

Once a secret reaches source control history, a push, a fork, or a CI log, it must be considered exposed. Remediation is rotate/revoke — removing the commit does not help because the value persists in history and every clone. Then add detection so it can't recur.
