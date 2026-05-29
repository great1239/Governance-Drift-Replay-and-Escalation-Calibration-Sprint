# Review Packet

## One-Line Summary

This project keeps the previous operational drift monitor intact and adds governance replay plus escalation calibration on top.

## Sprint Title Note

`7-4-3` is treated as the interview sequence: 7-day task, 4-day task, and final 3-day task.

It is not used as a technical rule. The implemented scope is operational drift monitoring, governance drift replay, execution pressure comparison, and escalation calibration.

## Architecture

```text
samples/00_default_example/input_updates.json
        |
        v
governance_replay.py
        |
        v
structured parsing + old taxonomy + deterministic replay + pressure comparison + escalation calibration
        |
        v
runtime outputs folder
samples evidence suite
```

## Inspectable Proof

- Default messy input: `samples/00_default_example/input_updates.json`
- Rule file: `escalation_rules.json`
- Rule explanation: `RULES.md`
- Active rule snapshots: `samples/*/rules_used.json`
- Curated evidence suite: `samples/`
- Sample parsed outputs: `samples/*/structured_updates.json`
- Sample replay proofs: `samples/*/replay_results.json`
- Sample pressure outputs: `samples/*/pressure_comparison.json`
- Sample CSV reports: `samples/*/escalation_report.csv`
- Sample dashboards: `samples/*/dashboard.html`
- Sample screenshots: `samples/*/screenshot.png`

## Sample Evidence

The `samples` folder contains focused proof cases:

- `01_aligned`: normal aligned case
- `02_missing_evidence`: observability/evidence drift
- `03_authority_drift`: missing approval and unauthorized actor
- `04_replay_mismatch`: replay drift
- `05_under_escalated`: escalation too low
- `06_over_escalated`: escalation too high
- `07_pressure_increase`: pressure comparison across runs
- `08_ambiguous_input`: vague/mangled input handling
- `09_conflict_handling`: multiple drift signals resolved by deterministic priority

Each sample includes the messy input, structured output, replay result, CSV, dashboard, screenshot, and notes.

## Previous Features Kept

- Raw operational updates are parsed into structured fields.
- The old operational taxonomy is still visible:
  - `aligned`
  - `replay-risk`
  - `authority-risk`
  - `observability-risk`
  - `integration-risk`
  - `unclear/incomplete`
- The four original metrics are still calculated:
  - structured
  - observable
  - deterministic
  - governance-safe
- Scheduled mode analyzes only new records after the last saved timestamp.
- Pressure comparison checks whether metric rates drop when record volume increases.
- Dashboard styling remains in a separate CSS file.
- The old behavior is preserved inside `governance_replay.py` and `governance_stream_generator.py` without duplicate wrapper scripts.

## What Is Parsed

Each messy update is converted into:

- case ID
- timestamp
- service
- system status
- blockers
- dependencies
- replay risks
- observability risks
- governance risks
- evidence state
- approval state
- actor authorization state
- replay state
- owner state
- dependency state
- drift labels
- secondary drift labels
- conflict resolution
- expected escalation
- actual escalation
- escalation calibration
- recommended action

## Pressure Comparison

This carries forward the useful part of the previous task.

Each run saves:

- total case count
- structured rate
- observable rate
- deterministic rate
- governance-safe rate
- drift counts
- calibration counts

The next run compares against that saved state. If case count increases, pressure increased. If any metric drops while pressure increased, the dashboard makes that visible.

## New Features Added

- Governance drift labels such as `authority-drift`, `replay-drift`, `evidence-drift`, and `escalation-drift`.
- Expected escalation is calculated from visible rules.
- The loaded rule config is written to `rules_used.json` for every run.
- Actual escalation is extracted from the update.
- Calibration is marked as `calibrated`, `under-escalated`, or `over-escalated`.
- The same selected input batch is replayed twice to prove deterministic output.

## Deterministic Rule Priority

If one update has multiple drift signals, primary drift is chosen in this order:

1. `authority-drift`
2. `replay-drift`
3. `escalation-drift`
4. `evidence-drift`
5. `ownership-drift`
6. `dependency-drift`
7. `ambiguous`
8. `aligned`

The priority is visible in `escalation_rules.json`.

The conflict proof is saved in `samples/09_conflict_handling`. Each row keeps all matching labels in `drift_types` and explains the selected primary label in `conflict_resolution`.

## Escalation Calibration

Escalation levels are ranked:

1. `none`
2. `service-owner`
3. `team-lead`
4. `incident-commander`
5. `governance-review`

The program marks each case as:

- `calibrated`
- `under-escalated`
- `over-escalated`

## Failure Handling

- Vague input becomes `ambiguous`.
- Missing evidence becomes `evidence-drift`.
- Approval or authorization problems become `authority-drift`.
- Replay mismatch becomes `replay-drift`.
- Wrong escalation level becomes `escalation-drift`.
- Malformed JSON stops the run instead of guessing.

## Final Reflection

The safest operational output is not the most fluent explanation. It is the one that can be replayed, inspected, and challenged.

This project keeps the system bounded by using explicit rules, visible outputs, and deterministic replay instead of open-ended generation.
