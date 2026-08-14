MATCH (a:Person)-[:KNOWS*1..3]->(b:Person)
RETURN b
