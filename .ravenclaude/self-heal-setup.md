# Self-heal setup — corrected (optional)

## What went wrong with the first command (my mistake)
I invented a `/rulesets/{id}/bypass-actors` POST endpoint — **it doesn't exist** (that's the 404). Bypass actors
live *inside* the ruleset object, so you update them by **PUT-ing the whole ruleset back** with the actor added.

## The real blocker (diagnosed this session)
The corrected PUT returns **HTTP 403** with header `X-Accepted-Github-Permissions: administration=write`.
Meaning: the **Codespace `GITHUB_TOKEN`** (what `gh` uses inside the Codespace terminal) **lacks `administration:write`**.
So running this *in the Codespace terminal will keep failing* regardless of the command — it's a token-scope problem,
not a command problem.

## To actually do it — run with an admin-scoped token

**Easiest: from your local machine** (where `gh auth login` is your own account = repo admin), OR with a
**fine-grained PAT** that has **Repository permissions → Administration: Read and write** on `mcorbett51090/RavenClaude`,
exported as `GH_TOKEN`. Then paste this **safe, idempotent** script (it preserves the entire existing ruleset and
only *adds* the GitHub Actions app — it never rewrites your rules):

```bash
RS=$(gh api /repos/mcorbett51090/RavenClaude/rulesets/17278731)
echo "$RS" | python3 -c '
import json,sys
d=json.load(sys.stdin)
ba=d.get("bypass_actors",[])
if not any(a.get("actor_id")==15368 for a in ba):
    ba.append({"actor_id":15368,"actor_type":"Integration","bypass_mode":"always"})
body={k:d[k] for k in ("name","target","enforcement","conditions","rules") if k in d}
body["bypass_actors"]=ba
json.dump(body,open("/tmp/ruleset-put.json","w"))
print("will set bypass actors:",[a["actor_id"] for a in ba])
'
gh api --method PUT /repos/mcorbett51090/RavenClaude/rulesets/17278731 --input /tmp/ruleset-put.json \
  --jq '.bypass_actors[] | select(.actor_id==15368)'
```

A line showing `15368 / Integration / always` = success.

## Verify (read-only, works with any token)
```bash
gh api /repos/mcorbett51090/RavenClaude/rulesets/17278731 \
  --jq '.bypass_actors[] | select(.actor_id==15368)'
```

---

**Reminder: this is optional and does NOT block today's Learn-tab work** (that renders fine locally). It only
makes `main` self-heal generated-artifact drift automatically. The current ruleset already has 5 bypass actors
(RepositoryRole + 4 Integration apps); this adds the GitHub Actions app (15368) as a 6th. Reversible — re-run the
script with the `append` line removed to take it back out. Tell me when it's applied and I'll flip
`regenerate-artifacts.yml` to push-on-merge + verify end-to-end.
