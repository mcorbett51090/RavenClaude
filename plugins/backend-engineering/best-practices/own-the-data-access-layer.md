# Own the data-access layer behind a repository

Keep persistence behind a repository/data-mapper with explicit, short transaction boundaries rather than scattering raw ORM calls through controllers and use-cases. This is the single place where N+1 queries, accidental long transactions, and missing indexes are introduced — concentrating it makes those defects visible and fixable, and keeps business logic free of persistence concerns.
