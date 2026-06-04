# Metric definition (metrics-as-code, pattern)

```yaml
metrics:
  - name: revenue
    description: "Recognized net revenue"
    type: simple
    type_params: { measure: net_revenue_amount }
    # grain + filters EXPLICIT
    filter: "{{ Dimension('order__status') }} = 'completed'"
```

- One definition, consumed by every BI tool.
- Grain + filters stated. Versioned, PR-reviewed.
