# Govern event schemas with a registry

Register event schemas and enforce compatibility rules (backward/forward) so a producer change can't silently break every consumer, and evolve schemas additively. An unversioned, ungoverned event payload is a cross-team outage waiting to happen: the producer ships a 'small change', and consumers deserializing the old shape fail in production with no warning.
