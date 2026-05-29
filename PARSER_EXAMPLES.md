# Parser Examples

This file shows raw input converted into structured output. The examples are copied from the saved sample artifacts.

## Example 1: Authority Drift

Input source:
[samples/03_authority_drift/input_updates.json](samples/03_authority_drift/input_updates.json)

Raw update:

```text
Payments manual override completed without approval by unauthorized contractor. No escalation.
```

Parsed output:

```json
{
  "case_id": "S03-002",
  "system_status": "unknown",
  "approval_state": "unsafe",
  "actor_authorized": "no",
  "drift_types": ["authority-drift", "escalation-drift"],
  "primary_drift": "authority-drift",
  "operational_drift_classification": "authority-risk",
  "expected_escalation": "governance-review",
  "actual_escalation": "none",
  "calibration": "under-escalated"
}
```

Saved output:
[samples/03_authority_drift/structured_updates.json](samples/03_authority_drift/structured_updates.json)

## Example 2: Missing Evidence

Input source:
[samples/02_missing_evidence/input_updates.json](samples/02_missing_evidence/input_updates.json)

Raw update:

```text
Billing latency spike in production. No trace and no evidence attached. Escalated to incident commander.
```

Parsed output:

```json
{
  "case_id": "S02-002",
  "system_status": "degraded",
  "evidence_state": "missing",
  "drift_types": ["evidence-drift"],
  "primary_drift": "evidence-drift",
  "operational_drift_classification": "observability-risk",
  "expected_escalation": "incident-commander",
  "actual_escalation": "incident-commander",
  "calibration": "calibrated"
}
```

Saved output:
[samples/02_missing_evidence/structured_updates.json](samples/02_missing_evidence/structured_updates.json)

## Example 3: Replay Mismatch

Input source:
[samples/04_replay_mismatch/input_updates.json](samples/04_replay_mismatch/input_updates.json)

Raw update:

```text
Search replay mismatch after rerun. Different result from the same input. Evidence attached. Escalated to team lead.
```

Parsed output:

```json
{
  "case_id": "S04-002",
  "evidence_state": "present",
  "replay_state": "mismatch",
  "replay_risks": ["replay mismatch"],
  "drift_types": ["replay-drift"],
  "primary_drift": "replay-drift",
  "operational_drift_classification": "replay-risk",
  "expected_escalation": "team-lead",
  "actual_escalation": "team-lead",
  "calibration": "calibrated"
}
```

Saved output:
[samples/04_replay_mismatch/structured_updates.json](samples/04_replay_mismatch/structured_updates.json)

## Example 4: Multiple Risks In One Update

Input source:
[samples/09_conflict_handling/input_updates.json](samples/09_conflict_handling/input_updates.json)

Raw update:

```text
Payments production fix used manual override without approval by unauthorized contractor. Missing trace. Replay mismatch. Blocked by database. No owner. No escalation.
```

Parsed output:

```json
{
  "case_id": "S09-001",
  "system_status": "blocked",
  "blockers": ["blocked"],
  "dependencies": ["blocked by", "database"],
  "replay_risks": ["replay mismatch"],
  "observability_risks": ["missing trace"],
  "governance_risks": ["without approval", "unauthorized", "manual override"],
  "drift_types": [
    "authority-drift",
    "replay-drift",
    "evidence-drift",
    "ownership-drift",
    "dependency-drift",
    "escalation-drift"
  ],
  "primary_drift": "authority-drift",
  "conflict_resolution": "authority-drift selected by drift_priority over replay-drift, evidence-drift, ownership-drift, dependency-drift, escalation-drift"
}
```

Saved output:
[samples/09_conflict_handling/structured_updates.json](samples/09_conflict_handling/structured_updates.json)
