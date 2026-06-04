# GCP resource hierarchy

```
organization
├── folder: prod
│   ├── project: app-prod
│   └── project: data-prod
├── folder: non-prod
│   └── project: app-dev
└── folder: shared
    ├── project: network-host (Shared VPC)
    └── project: logging
```

**Org policy (set at org/folder):** restrict regions · disable SA key creation · no external IP · OS Login
**Build:** terraform-iac
