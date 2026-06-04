# Put integrity constraints in the database

Primary keys, foreign keys, NOT NULL, UNIQUE, and CHECK constraints belong in the schema, not solely in application code. The database is the single point through which all writes pass and the only reliable enforcer; application-only validation is bypassed by every other writer, migration, and bug. Make illegal states unrepresentable at the storage layer.
