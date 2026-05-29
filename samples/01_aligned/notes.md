# 01 Aligned

Purpose: shows a 10-update clean batch where the updates are structured, observable, deterministic, and governance-safe.

Input signal:

```text
Trace attached. Evidence attached. Approval granted. Replay matched. No escalation required.
```

Expected result:

```text
all target rows should remain aligned
expected_escalation = none
actual_escalation = none
calibration = calibrated
```

Reproduction command:

```powershell
python governance_replay.py --input samples/01_aligned/input_updates.json --output-dir samples/01_aligned --full --no-open
```
