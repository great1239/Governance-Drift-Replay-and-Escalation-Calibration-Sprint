# Sample Evidence Suite

This folder contains inspectable proof cases. Each sample starts with messy input and includes the generated JSON, CSV, dashboard, screenshot, and notes.

## Start Here

Open the default example first:

- [Default notes](00_default_example/notes.md)
- [Default input](00_default_example/input_updates.json)
- [Default dashboard](00_default_example/dashboard.html)
- [Default screenshot](00_default_example/screenshot.png)

## Scenario Index

### 00 Default Example

Covers: general/default run  
Input size: 7  
Main proof: complete output set  
Notes: [notes](00_default_example/notes.md)  
Input: [input](00_default_example/input_updates.json)  
Dashboard: [dashboard](00_default_example/dashboard.html)  
Screenshot: [screenshot](00_default_example/screenshot.png)

### 01 Aligned

Covers: aligned behavior  
Input size: 10  
Main proof: no drift expected  
Notes: [notes](01_aligned/notes.md)  
Input: [input](01_aligned/input_updates.json)  
Dashboard: [dashboard](01_aligned/dashboard.html)  
Screenshot: [screenshot](01_aligned/screenshot.png)

### 02 Missing Evidence

Covers: missing evidence  
Input size: 10  
Main proof: `evidence-drift` / `observability-risk`  
Notes: [notes](02_missing_evidence/notes.md)  
Input: [input](02_missing_evidence/input_updates.json)  
Dashboard: [dashboard](02_missing_evidence/dashboard.html)  
Screenshot: [screenshot](02_missing_evidence/screenshot.png)

### 03 Authority Drift

Covers: approval and authorization failure  
Input size: 10  
Main proof: `authority-drift` / `authority-risk`  
Notes: [notes](03_authority_drift/notes.md)  
Input: [input](03_authority_drift/input_updates.json)  
Dashboard: [dashboard](03_authority_drift/dashboard.html)  
Screenshot: [screenshot](03_authority_drift/screenshot.png)

### 04 Replay Mismatch

Covers: replay mismatch  
Input size: 10  
Main proof: `replay-drift` / `replay-risk`  
Notes: [notes](04_replay_mismatch/notes.md)  
Input: [input](04_replay_mismatch/input_updates.json)  
Dashboard: [dashboard](04_replay_mismatch/dashboard.html)  
Screenshot: [screenshot](04_replay_mismatch/screenshot.png)

### 05 Under Escalated

Covers: escalation too low  
Input size: 10  
Main proof: `under-escalated`  
Notes: [notes](05_under_escalated/notes.md)  
Input: [input](05_under_escalated/input_updates.json)  
Dashboard: [dashboard](05_under_escalated/dashboard.html)  
Screenshot: [screenshot](05_under_escalated/screenshot.png)

### 06 Over Escalated

Covers: escalation too high  
Input size: 10  
Main proof: `over-escalated`  
Notes: [notes](06_over_escalated/notes.md)  
Input: [input](06_over_escalated/input_updates.json)  
Dashboard: [dashboard](06_over_escalated/dashboard.html)  
Screenshot: [screenshot](06_over_escalated/screenshot.png)

### 07 Pressure Increase

Covers: pressure comparison  
Input size: 10  
Main proof: pressure increases from 4 to 6 new records  
Notes: [notes](07_pressure_increase/notes.md)  
Input: [input](07_pressure_increase/input_updates.json)  
Dashboard: [dashboard](07_pressure_increase/dashboard.html)  
Screenshot: [screenshot](07_pressure_increase/screenshot.png)

### 08 Ambiguous Input

Covers: vague/mangled input  
Input size: 10  
Main proof: `ambiguous` / `unclear/incomplete`  
Notes: [notes](08_ambiguous_input/notes.md)  
Input: [input](08_ambiguous_input/input_updates.json)  
Dashboard: [dashboard](08_ambiguous_input/dashboard.html)  
Screenshot: [screenshot](08_ambiguous_input/screenshot.png)

## What Each Sample Contains

Most sample folders contain:

```text
input_updates.json
structured_updates.json
replay_results.json
pressure_comparison.json
escalation_report.csv
dashboard.html
dashboard.css
screenshot.png
notes.md
```

`07_pressure_increase` also includes:

```text
baseline_input_updates.json
last_run_state.json
```

Those two files are needed because pressure comparison is a two-run scenario.

## Reproduction Pattern

For any one-run sample:

```powershell
python governance_replay.py --input samples/03_authority_drift/input_updates.json --output-dir samples/03_authority_drift --full --no-open
```

For the pressure sample:

```powershell
python governance_replay.py --input samples/07_pressure_increase/baseline_input_updates.json --output-dir samples/07_pressure_increase --state-file samples/07_pressure_increase/last_run_state.json
python governance_replay.py --input samples/07_pressure_increase/input_updates.json --output-dir samples/07_pressure_increase --state-file samples/07_pressure_increase/last_run_state.json
```
