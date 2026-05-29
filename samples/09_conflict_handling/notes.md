# 09 Conflict Handling

Purpose: shows what happens when one update contains multiple drift signals at the same time.

Input signal:

```text
without approval + unauthorized + missing trace + replay mismatch + blocked by database + no owner
```

Expected result:

```text
all matching drift labels are kept in drift_types
primary_drift is chosen by escalation_rules.json priority
authority-drift wins over replay/evidence/dependency/ownership conflicts
replay-drift wins over evidence/dependency conflicts when authority is absent
calibration is still checked after the primary drift is chosen
```

Priority used:

```text
authority-drift
replay-drift
escalation-drift
evidence-drift
ownership-drift
dependency-drift
ambiguous
aligned
```

Reproduction command:

```powershell
python governance_replay.py --input samples/09_conflict_handling/input_updates.json --output-dir samples/09_conflict_handling --full --no-open
```
