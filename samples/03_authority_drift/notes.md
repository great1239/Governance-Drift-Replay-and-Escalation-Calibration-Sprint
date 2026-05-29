# 03 Authority Drift

Purpose: shows a 10-update batch with missing approval and unauthorized execution mixed with normal updates.

Input signal:

```text
manual override completed without approval by unauthorized contractor
```

Expected result:

```text
target rows include authority-drift
operational_drift_classification = authority-risk
expected_escalation = governance-review
calibration includes under-escalated cases
```

Reproduction command:

```powershell
python governance_replay.py --input samples/03_authority_drift/input_updates.json --output-dir samples/03_authority_drift --full --no-open
```
