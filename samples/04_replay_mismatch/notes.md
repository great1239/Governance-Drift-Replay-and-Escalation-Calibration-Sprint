# 04 Replay Mismatch

Purpose: shows a 10-update batch with replay mismatch cases mixed with normal updates.

Input signal:

```text
Replay mismatch after rerun. Different result from the same input.
```

Expected result:

```text
target rows include replay-drift
operational_drift_classification = replay-risk
expected_escalation = team-lead
calibration includes calibrated replay-risk examples
```

Reproduction command:

```powershell
python governance_replay.py --input samples/04_replay_mismatch/input_updates.json --output-dir samples/04_replay_mismatch --full --no-open
```
