# 06 Over Escalated

Purpose: shows a 10-update batch where some safe cases are escalated higher than expected.

Input signal:

```text
stable ... Approval granted ... Replay passed. Escalated to governance review.
```

Expected result:

```text
target rows include escalation-drift
expected_escalation = none
actual escalation is higher than expected
calibration = over-escalated
```

Reproduction command:

```powershell
python governance_replay.py --input samples/06_over_escalated/input_updates.json --output-dir samples/06_over_escalated --full --no-open
```
