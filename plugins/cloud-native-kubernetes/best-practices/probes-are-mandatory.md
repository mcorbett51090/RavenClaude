# Configure all three probe types correctly

Liveness restarts a hung container, readiness gates traffic until the pod can serve, and startup protects a slow boot from a premature liveness kill. Missing or mis-tuned probes cause both phantom restart loops and traffic routed to pods that can't serve it.
