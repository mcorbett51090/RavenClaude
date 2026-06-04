# Use the organization → folders → projects hierarchy

GCP's hierarchy is where IAM and org policy inherit and where blast radius and billing are bounded. Group projects under folders by environment/department and keep one project per app/workload. A flat pile of resources in one project is GCP's equivalent of one giant cloud account: no isolation, no clean billing, and policy you can't apply by inheritance.
