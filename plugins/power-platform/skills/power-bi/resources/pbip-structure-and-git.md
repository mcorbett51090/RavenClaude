# PBIP Structure and Git / Azure DevOps Integration

## Recommended Folder Structure (PBIP)
- MyReport.pbip (the project file)
- SemanticModel/ (definition files — prefer .tmdl or clean JSON where possible)
- Report/ (visuals, pages, bookmarks, etc.)
- .pbit files as needed

## Git Best Practices
- **Commit the PBIP tree**, never the binary .pbix.
- Use a sensible .gitignore (exclude caches, temp exports, large binaries, .pbix backups).
- For large models: consider splitting via composite models or views to keep diffs manageable.
- Parameterize connections and use Deployment Rules in pipelines rather than maintaining multiple branches.
- Review diffs on model definition and measures more carefully than on report layout JSON.

## Common ADO / Git Pain Points
- Large JSON diffs on every small change.
- Merge conflicts in model files (resolve by re-exporting clean from Desktop or using Tabular Editor).
- Hard-coded workspace/dataset IDs or gateway references in scripts or reports.
- Forgetting that Deployment Pipelines have their own rules for parameters and connections.

## Recommendation
Start with trunk-based or short-lived feature branches. Require `pac solution check` equivalent or Power BI validation in PR pipelines where possible. Coordinate with `solution-alm-engineer` when Power BI artifacts are part of a larger solution promotion.