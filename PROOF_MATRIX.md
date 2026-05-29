# Operational Proof Matrix

This file points to inspectable artifacts instead of restating claims.

## Requirement-To-Proof Map

| Requirement | Concrete Proof | What To Check |
|---|---|---|
| Messy input is accepted | [samples/03_authority_drift/input_updates.json](samples/03_authority_drift/input_updates.json) | Raw text such as `manual override completed without approval by unauthorized contractor` |
| Raw input is parsed into structured fields | [samples/03_authority_drift/structured_updates.json](samples/03_authority_drift/structured_updates.json) | Case `S03-002` has `approval_state: unsafe`, `actor_authorized: no`, `primary_drift: authority-drift` |
| System status is parsed | [samples/02_missing_evidence/structured_updates.json](samples/02_missing_evidence/structured_updates.json) | Case `S02-002` has `system_status: degraded` |
| Blockers are parsed | [samples/09_conflict_handling/structured_updates.json](samples/09_conflict_handling/structured_updates.json) | Case `S09-001` has `blockers: ["blocked"]` |
| Dependencies are parsed | [samples/09_conflict_handling/structured_updates.json](samples/09_conflict_handling/structured_updates.json) | Case `S09-001` has `dependencies: ["blocked by", "database"]` |
| Replay risks are parsed | [samples/04_replay_mismatch/structured_updates.json](samples/04_replay_mismatch/structured_updates.json) | Case `S04-002` has `replay_state: mismatch` and `replay_risks: ["replay mismatch"]` |
| Observability risks are parsed | [samples/02_missing_evidence/structured_updates.json](samples/02_missing_evidence/structured_updates.json) | Case `S02-002` has `evidence_state: missing` |
| Governance risks are parsed | [samples/03_authority_drift/structured_updates.json](samples/03_authority_drift/structured_updates.json) | Case `S03-002` has `governance_risks` and `authority-drift` |
| Drift classification is visible | [samples/README.md](samples/README.md) | Each sample maps to a drift/calibration scenario |
| Conflict handling is deterministic | [samples/09_conflict_handling/structured_updates.json](samples/09_conflict_handling/structured_updates.json) | Case `S09-001` keeps all drift labels but selects `authority-drift` as primary |
| Rule config is visible | [RULES.md](RULES.md), [escalation_rules.json](escalation_rules.json), [samples/00_default_example/rules_used.json](samples/00_default_example/rules_used.json) | Human-readable rules, machine config, and per-run snapshot all exist |
| Escalation calibration is visible | [samples/05_under_escalated/structured_updates.json](samples/05_under_escalated/structured_updates.json), [samples/06_over_escalated/structured_updates.json](samples/06_over_escalated/structured_updates.json) | Case `S05-002` is `under-escalated`; case `S06-002` is `over-escalated` |
| Deterministic replay is checked | [samples/00_default_example/replay_results.json](samples/00_default_example/replay_results.json) | `summary.deterministic_replay_pass` is recorded |
| Execution pressure comparison is shown | [samples/07_pressure_increase/pressure_comparison.json](samples/07_pressure_increase/pressure_comparison.json) | Pressure increases from `4` to `6` analyzed cases and metric deltas drop |
| Dashboard proof exists | [samples/03_authority_drift/dashboard.html](samples/03_authority_drift/dashboard.html), [samples/03_authority_drift/screenshot.png](samples/03_authority_drift/screenshot.png) | HTML dashboard plus full-page screenshot |
| Malformed input is rejected | [samples/10_malformed_json/bad_updates.json](samples/10_malformed_json/bad_updates.json), [samples/10_malformed_json/expected_error.txt](samples/10_malformed_json/expected_error.txt) | Program exits with a JSON parse error instead of guessing |

## Concrete Pressure Proof

From [samples/07_pressure_increase/pressure_comparison.json](samples/07_pressure_increase/pressure_comparison.json):

```json
{
  "previous_total_cases": 4,
  "current_total_cases": 6,
  "pressure_direction": "increased",
  "stable_under_pressure": false,
  "metric_deltas": {
    "structured": -50.0,
    "observable": -50.0,
    "deterministic": -16.67,
    "governance_safe": -8.33
  }
}
```

This is the execution-pressure proof. The program does not merely count drift; it compares whether the operating metrics remain stable when the amount of analyzed work increases.

## Concrete Conflict Proof

From [samples/09_conflict_handling/structured_updates.json](samples/09_conflict_handling/structured_updates.json), case `S09-001`:

```json
{
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

This shows the conflict handling rule in operation.
