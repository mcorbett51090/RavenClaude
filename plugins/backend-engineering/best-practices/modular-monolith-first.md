# Start with a modular monolith

Begin with a single well-modularized deployable and split into services only when a concrete need appears — independent scaling, team autonomy, deploy isolation, or a genuine tech/runtime boundary. Premature microservices impose network latency, partial failure, eventual consistency, and operational overhead with none of the benefits, and a 'microservices' system sharing one database is just a distributed monolith.
