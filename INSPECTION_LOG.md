# Inspection Log

This file records observed outputs from the current repository artifacts.

## Commands Checked

Python compile check:

```text
Command: python -m py_compile governance_replay.py governance_stream_generator.py
Exit code: 0
Output: none
```

Default run:

```text
Command: python governance_replay.py --full --no-open
Exit code: 0

Governance replay complete
- structured output: outputs\structured_updates.json
- replay output:     outputs\replay_results.json
- pressure output:   outputs\pressure_comparison.json
- rules used:        outputs\rules_used.json
- csv report:        outputs\escalation_report.csv
- dashboard:         outputs\dashboard.html
- deterministic replay pass: True
- analyzed records: 7 of 7
```

Malformed JSON run:

```text
Command: python governance_replay.py --input samples/10_malformed_json/bad_updates.json --full --no-open
Exit code: 1

Could not read valid JSON from samples\10_malformed_json\bad_updates.json: Expecting ',' delimiter: line 10 column 5 (char 210)
```

## Sample Artifact Inventory

```text
00_default_example: input=7, analyzed=7, deterministic=True, dashboard=True, screenshot=1440x2522, pressure=not-tracked
01_aligned: input=10, analyzed=10, deterministic=True, dashboard=True, screenshot=1440x2730, pressure=not-tracked
02_missing_evidence: input=10, analyzed=10, deterministic=True, dashboard=True, screenshot=1440x2955, pressure=not-tracked
03_authority_drift: input=10, analyzed=10, deterministic=True, dashboard=True, screenshot=1440x2956, pressure=not-tracked
04_replay_mismatch: input=10, analyzed=10, deterministic=True, dashboard=True, screenshot=1440x2993, pressure=not-tracked
05_under_escalated: input=10, analyzed=10, deterministic=True, dashboard=True, screenshot=1440x2842, pressure=not-tracked
06_over_escalated: input=10, analyzed=10, deterministic=True, dashboard=True, screenshot=1440x2842, pressure=not-tracked
07_pressure_increase: input=10, analyzed=6, deterministic=True, dashboard=True, screenshot=1440x2386, pressure=increased
08_ambiguous_input: input=10, analyzed=10, deterministic=True, dashboard=True, screenshot=1440x2767, pressure=not-tracked
09_conflict_handling: input=10, analyzed=10, deterministic=True, dashboard=True, screenshot=1440x3403, pressure=not-tracked
10_malformed_json: failure-only, files=3
```

## Parsed Case Checks

Authority case:

```text
File: samples/03_authority_drift/structured_updates.json
Case: S03-002
approval_state: unsafe
actor_authorized: no
primary_drift: authority-drift
secondary_drifts: ['escalation-drift']
expected_escalation: governance-review
actual_escalation: none
calibration: under-escalated
safe_to_continue: False
```

Replay mismatch case:

```text
File: samples/04_replay_mismatch/structured_updates.json
Case: S04-002
evidence_state: present
replay_state: mismatch
primary_drift: replay-drift
expected_escalation: team-lead
actual_escalation: team-lead
calibration: calibrated
safe_to_continue: False
```

Conflict case:

```text
File: samples/09_conflict_handling/structured_updates.json
Case: S09-001
system_status: blocked
evidence_state: missing
approval_state: unsafe
actor_authorized: no
replay_state: mismatch
owner_state: missing
dependency_state: blocked
primary_drift: authority-drift
secondary_drifts: ['replay-drift', 'evidence-drift', 'ownership-drift', 'dependency-drift', 'escalation-drift']
conflict_resolution: authority-drift selected by drift_priority over replay-drift, evidence-drift, ownership-drift, dependency-drift, escalation-drift
expected_escalation: governance-review
actual_escalation: none
calibration: under-escalated
safe_to_continue: False
```

Pressure comparison:

```text
File: samples/07_pressure_increase/pressure_comparison.json
previous_total_cases: 4
current_total_cases: 6
pressure_direction: increased
stable_under_pressure: False
metric_deltas: {'structured': -50.0, 'observable': -50.0, 'deterministic': -16.67, 'governance_safe': -8.33}
```
