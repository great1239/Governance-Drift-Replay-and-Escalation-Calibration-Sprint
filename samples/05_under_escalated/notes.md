# 05 Under Escalated

Purpose: shows a 10-update batch where some high-severity cases are escalated below the expected level.

Input signal:

```text
critical outage in production ... Escalated to service owner.
```

Expected result:

```text
target rows include escalation-drift
expected_escalation = incident-commander
actual escalation is lower than expected
calibration = under-escalated
```

Reproduction command:

```powershell
python governance_replay.py --input samples/05_under_escalated/input_updates.json --output-dir samples/05_under_escalated --full --no-open
```
