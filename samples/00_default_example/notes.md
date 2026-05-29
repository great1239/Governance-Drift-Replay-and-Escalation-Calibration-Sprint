# 00 Default Example

Purpose: shows the default project input and the complete set of generated outputs.

This folder uses a copy of the root `input_updates.json` file. It is the general example to open first.

Reproduction command:

```powershell
python governance_replay.py --input samples/00_default_example/input_updates.json --output-dir samples/00_default_example --full --no-open
```

Generated outputs:

- `structured_updates.json`
- `replay_results.json`
- `pressure_comparison.json`
- `escalation_report.csv`
- `dashboard.html`
- `dashboard.css`
- `screenshot.png`
