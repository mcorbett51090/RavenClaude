# GitHub API Best Practices & Rate Limit Guidelines

> Updated guidance for reliable file updates across RavenClaude projects.

## Rate Limits

- Primary limit: 5,000 requests/hour (account-wide)
- Secondary limits and abuse detection are the main practical constraints.
- **Rule**: Space write operations (minimum 3 seconds between calls). Max ~5 writes per minute when possible.

## File Update Strategy (Important Update)

### Recommended Approach by File Size

| File Type / Size          | Recommended Method          | Reason |
|---------------------------|-----------------------------|--------|
| Small files / Configs     | Contents API (`create_or_update_file`) | Simple and sufficient |
| **Medium to Large files** (e.g. HTML, JS, full apps) | **Regular Git push** | Much more reliable. Contents API can truncate or fail with larger payloads |
| Very large or binary files| Git + Git LFS               | Standard industry practice |

### Why We Prefer Git for Larger Files

- The Contents API has practical limitations with bigger files.
- Repeated or large `create_or_update_file` calls are more likely to hit secondary rate limits or return incomplete content.
- Using normal Git workflow (clone → edit → commit → push) is the most common and reliable pattern used by developers and automation tools.

## Updated Rules

- Use the **Contents API** only for small files and configuration.
- For anything substantial (like full HTML/JS applications), prepare changes locally and push via Git.
- When using the API, always space calls and batch when possible.
- If hitting issues with large files via API, switch to Git-based updates.

## For RavenClaude Projects

This guidance applies to all repositories involving automation, agents, or frequent file updates.

---

*Maintained to improve reliability across projects.*