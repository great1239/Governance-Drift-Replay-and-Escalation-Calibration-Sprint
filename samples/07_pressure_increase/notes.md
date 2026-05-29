# 07 Pressure Increase

Purpose: shows scheduled pressure comparison. The first run has 4 records. The second run sees 6 new records, so pressure increases.

Input signal:

```text
baseline = 4 clean updates
next run = 6 new mixed-risk updates
```

Expected result:

```text
pressure_direction = increased
previous_total_cases = 4
current_total_cases = 6
stable_under_pressure = false
```

Reproduction commands:

```powershell
python governance_replay.py --input samples/07_pressure_increase/baseline_input_updates.json --output-dir samples/07_pressure_increase --state-file samples/07_pressure_increase/last_run_state.json
python governance_replay.py --input samples/07_pressure_increase/input_updates.json --output-dir samples/07_pressure_increase --state-file samples/07_pressure_increase/last_run_state.json
```
