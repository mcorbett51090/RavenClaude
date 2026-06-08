# Per-device identity, never a shared fleet secret

Every device gets a unique identity — an X.509 certificate or key held in a secure element — provisioned at manufacture or first boot, with a rotation/revocation story. A fleet that shares one provisioning secret is one extraction away from total compromise: pull the key off a single unit and you can clone or impersonate every device. Likewise, never ship a hardcoded TLS/PSK key or `verify=false`; use mutual TLS/DTLS with per-device credentials, or a named, security-reviewed exception — never a silent shortcut.
