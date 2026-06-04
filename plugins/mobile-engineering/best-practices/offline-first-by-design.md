# Design offline-first from day one

On mobile the network is intermittent by nature, so design for offline reads, queued offline writes, and an explicit conflict-resolution policy before writing features — with a local database as the source of truth that syncs to the server. Bolting offline support onto an always-online architecture later is effectively a rewrite, because it changes where truth lives and how every mutation flows.
