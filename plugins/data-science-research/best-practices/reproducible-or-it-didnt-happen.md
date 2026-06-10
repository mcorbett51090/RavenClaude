# Reproducible or it didn't happen

A result that can't be re-run from a pinned environment, a versioned dataset, and a fixed seed is an anecdote. Pin Python and every dependency in a lockfile (a floating `>=` is a future irreproducibility), version the exact input data with a hash or snapshot (never "the latest table"), set and thread random seeds through every stochastic step, and clean the notebook to run top-to-bottom — or extract it to a scripted pipeline. Track each run's params, metrics, and the code+data version so any result is recoverable and comparable.
