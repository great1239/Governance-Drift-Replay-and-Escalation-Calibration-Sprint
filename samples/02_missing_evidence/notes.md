# 02 Missing Evidence

Purpose: shows a 10-update batch with several missing trace/evidence cases mixed with normal updates.

Input signal:

```text
No trace and no evidence attached.
```

Expected result:

```text
target rows include evidence-drift
operational_drift_classification = observability-risk
calibration includes calibrated evidence-risk examples
```

Reproduction command:

```powershell
python governance_replay.py --input samples/02_missing_evidence/input_updates.json --output-dir samples/02_missing_evidence --full --no-open
```
