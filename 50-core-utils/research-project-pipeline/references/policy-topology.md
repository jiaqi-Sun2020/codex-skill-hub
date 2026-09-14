# Mandatory-Policy Topology

Use this declaration when a project has nested directories from which an Agent
or command can be started independently, or when a mandatory rule is not local
to every execution root.

The pipeline can discover `.agents/AGENTS.md` and legacy `.agent/AGENTS.md`
entrypoints, but it cannot infer from filenames which prose is mandatory. The
declaration supplies that missing authority without copying the policy body.

## Minimal explicit-reference example

```json
{
  "schema_version": "research-policy-topology/v1",
  "execution_roots": [
    {"id": "root", "path": "."},
    {"id": "analysis", "path": "analysis"}
  ],
  "policies": [
    {
      "id": "experiment-audit",
      "path": ".agents/EXPERIMENT_AUDIT_PROTOCOL.md",
      "sha256": "<64 hexadecimal characters>",
      "mandatory": true,
      "applies_to": ["analysis"]
    }
  ],
  "bindings": [
    {
      "execution_root_id": "analysis",
      "policy_id": "experiment-audit",
      "type": "explicit_reference",
      "non_weakening": true,
      "semantic_review": {
        "status": "approved",
        "reviewer": "owner-name",
        "reviewed_at": "YYYY-MM-DD"
      }
    }
  ]
}
```

`analysis/.agents/AGENTS.md` must contain the canonical relative path computed
from the execution root to the policy. The short reference should state that
local instructions supplement and must not weaken the canonical policy.

## Binding types

- `explicit_reference`: the execution root's `AGENTS.md` contains the canonical
  relative policy path. `non_weakening=true` records the intended constraint;
  an approved semantic review is required because prose strength cannot be
  proved from path reachability.
- `verified_loader`: identify the project-contained loader and a passing,
  immutable verification-evidence file; both require SHA-256 values. The
  evidence must explicitly name the covered execution-root and policy IDs.
- `owner_approved_isolation`: record owner, date, and rationale. Isolation is a
  visible exception and leaves the result conditional rather than pretending
  the policy was loaded.

`applies_to` contains execution-root IDs or `"*"`. An applicable mandatory
policy with no valid binding is unsafe. Unknown scope IDs, broken paths, link
traversal, hash drift, and mandatory policies stored only in optional memory are
also unsafe.

If an existing policy body was copied historically, list its project-relative
path in that policy's optional `known_copies`. Auditors compare only declared
copies: a matching filename alone is not enough evidence that two files share
policy identity.

Read [policy-topology.schema.json](policy-topology.schema.json) for the complete
machine shape. The pipeline and Neat-Freak evaluate the declaration separately;
agreement between them is stronger evidence than either report alone.
