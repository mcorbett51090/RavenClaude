# Pool database connections

Front the database with a connection pooler sized to the workload. Databases handle a bounded number of connections efficiently and degrade badly past it; an application that opens a connection per request creates a thundering herd that exhausts the server under load. Pooling is the difference between graceful saturation and a connection-refused outage.
