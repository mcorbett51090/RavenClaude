# IaC repo layout (directory-per-environment example)

```
live/
  prod/
    network/   (its own state)
    data/      (its own state)
    app/       (its own state)
  staging/ ...
modules/
  network/  data/  app/   (versioned, reusable)
```

State isolated by blast radius + environment. Cross-state via remote-state data sources. Promotion = PR that bumps a module version / input.
