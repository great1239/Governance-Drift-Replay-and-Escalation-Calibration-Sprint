# Review Packet

This file is the reviewer shortcut. It explains what to inspect, what each artifact proves, how to reproduce the outputs, and what the project does not claim.

## Main Claim

Messy operational updates can be parsed into structured fields, classified with deterministic drift rules, checked for escalation calibration, replayed for consistency, and shown in inspectable dashboard/JSON/CSV outputs.

## One-Minute Review Path

1. Open the main README:
   [README.md](README.md)

2. Inspect the default dashboard:
   [samples/00_default_example/dashboard.html](samples/00_default_example/dashboard.html)

3. Inspect the default screenshot:
   [samples/00_default_example/screenshot.png](samples/00_default_example/screenshot.png)

4. Inspect the parsed JSON:
   [samples/00_default_example/structured_updates.json](samples/00_default_example/structured_updates.json)

5. Inspect the active rule snapshot:
   [samples/00_default_example/rules_used.json](samples/00_default_example/rules_used.json)

6. Inspect the proof matrix:
   [PROOF_MATRIX.md](PROOF_MATRIX.md)

7. Inspect raw-to-parsed examples:
   [PARSER_EXAMPLES.md](PARSER_EXAMPLES.md)

## How To Run

Run the default full example:

```powershell
python governance_replay.py --full --no-open
```

Run with your own update file:

```powershell
python governance_replay.py --input your_updates.json --full --no-open
```

Run in scheduled/stateful mode:

```powershell
python governance_replay.py --input samples/00_default_example/input_updates.json
```

Stateful mode analyzes only records newer than the previous saved timestamp and writes `outputs/last_run_state.json`.

## Core Files To Inspect

Main program:
[governance_replay.py](governance_replay.py)

Concrete proof matrix:
[PROOF_MATRIX.md](PROOF_MATRIX.md)

Raw-to-parsed examples:
[PARSER_EXAMPLES.md](PARSER_EXAMPLES.md)

Readable rule explanation:
[RULES.md](RULES.md)

Machine-readable rule config:
[escalation_rules.json](escalation_rules.json)

Optional messy test stream generator:
[governance_stream_generator.py](governance_stream_generator.py)

Dashboard stylesheet:
[dashboard.css](dashboard.css)

Sample evidence folder:
[samples/](samples/)

## Expected Runtime Outputs

When the program runs, it writes:

```text
outputs/structured_updates.json
outputs/replay_results.json
outputs/pressure_comparison.json
outputs/rules_used.json
outputs/escalation_report.csv
outputs/dashboard.html
outputs/dashboard.css
```

The runtime `outputs/` folder is git-ignored because curated proof outputs are already saved inside `samples/`.

## Assignment Coverage

Structured update parser:
The program parses messy text into case ID, timestamp, service, status, blockers, dependencies, replay risks, observability risks, governance risks, evidence state, approval state, authorization state, replay state, owner state, dependency state, drift labels, escalation fields, checks, and action.

Drift classification logic:
The program classifies into `aligned`, `authority-drift`, `replay-drift`, `escalation-drift`, `evidence-drift`, `ownership-drift`, `dependency-drift`, and `ambiguous`. It also preserves the earlier operational taxonomy: `aligned`, `replay-risk`, `authority-risk`, `observability-risk`, `integration-risk`, and `unclear/incomplete`.

Operational dashboard:
Each sample has `dashboard.html` and a full-page `screenshot.png`.

Governance summary:
Each dashboard contains the compressed run summary, drift counts, calibration counts, metric rates, pressure comparison, case replay results, and replay detail fields.

Rule/config visibility:
Rules are visible in `RULES.md`, `escalation_rules.json`, and every generated `rules_used.json`.

Operational proof density:
`PROOF_MATRIX.md` maps each requirement to a concrete file, case ID, and field. `PARSER_EXAMPLES.md` shows raw input converted into structured output.

Deterministic replay:
Each run evaluates the selected input twice and records whether both passes match.

Execution pressure comparison:
Stateful mode compares current run metrics against the previous run snapshot.

## Evidence Map

### 00 Default Example

Proves: baseline end-to-end run  
Notes: [notes](samples/00_default_example/notes.md)  
Input: [input](samples/00_default_example/input_updates.json)  
Parsed JSON: [structured output](samples/00_default_example/structured_updates.json)  
Dashboard: [dashboard](samples/00_default_example/dashboard.html)  
Screenshot: [screenshot](samples/00_default_example/screenshot.png)

### 01 Aligned

Proves: normal aligned behavior  
Notes: [notes](samples/01_aligned/notes.md)  
Input: [input](samples/01_aligned/input_updates.json)  
Parsed JSON: [structured output](samples/01_aligned/structured_updates.json)  
Dashboard: [dashboard](samples/01_aligned/dashboard.html)  
Screenshot: [screenshot](samples/01_aligned/screenshot.png)

### 02 Missing Evidence

Proves: observability/evidence drift  
Notes: [notes](samples/02_missing_evidence/notes.md)  
Input: [input](samples/02_missing_evidence/input_updates.json)  
Parsed JSON: [structured output](samples/02_missing_evidence/structured_updates.json)  
Dashboard: [dashboard](samples/02_missing_evidence/dashboard.html)  
Screenshot: [screenshot](samples/02_missing_evidence/screenshot.png)

### 03 Authority Drift

Proves: missing approval and unauthorized actor handling  
Notes: [notes](samples/03_authority_drift/notes.md)  
Input: [input](samples/03_authority_drift/input_updates.json)  
Parsed JSON: [structured output](samples/03_authority_drift/structured_updates.json)  
Dashboard: [dashboard](samples/03_authority_drift/dashboard.html)  
Screenshot: [screenshot](samples/03_authority_drift/screenshot.png)

### 04 Replay Mismatch

Proves: replay drift handling  
Notes: [notes](samples/04_replay_mismatch/notes.md)  
Input: [input](samples/04_replay_mismatch/input_updates.json)  
Parsed JSON: [structured output](samples/04_replay_mismatch/structured_updates.json)  
Dashboard: [dashboard](samples/04_replay_mismatch/dashboard.html)  
Screenshot: [screenshot](samples/04_replay_mismatch/screenshot.png)

### 05 Under Escalated

Proves: escalation lower than expected  
Notes: [notes](samples/05_under_escalated/notes.md)  
Input: [input](samples/05_under_escalated/input_updates.json)  
Parsed JSON: [structured output](samples/05_under_escalated/structured_updates.json)  
Dashboard: [dashboard](samples/05_under_escalated/dashboard.html)  
Screenshot: [screenshot](samples/05_under_escalated/screenshot.png)

### 06 Over Escalated

Proves: escalation higher than expected  
Notes: [notes](samples/06_over_escalated/notes.md)  
Input: [input](samples/06_over_escalated/input_updates.json)  
Parsed JSON: [structured output](samples/06_over_escalated/structured_updates.json)  
Dashboard: [dashboard](samples/06_over_escalated/dashboard.html)  
Screenshot: [screenshot](samples/06_over_escalated/screenshot.png)

### 07 Pressure Increase

Proves: stateful pressure comparison across two runs  
Notes: [notes](samples/07_pressure_increase/notes.md)  
Baseline input: [baseline input](samples/07_pressure_increase/baseline_input_updates.json)  
Second input: [input](samples/07_pressure_increase/input_updates.json)  
Pressure output: [pressure comparison](samples/07_pressure_increase/pressure_comparison.json)  
Dashboard: [dashboard](samples/07_pressure_increase/dashboard.html)  
Screenshot: [screenshot](samples/07_pressure_increase/screenshot.png)

### 08 Ambiguous Input

Proves: vague/mangled input handling  
Notes: [notes](samples/08_ambiguous_input/notes.md)  
Input: [input](samples/08_ambiguous_input/input_updates.json)  
Parsed JSON: [structured output](samples/08_ambiguous_input/structured_updates.json)  
Dashboard: [dashboard](samples/08_ambiguous_input/dashboard.html)  
Screenshot: [screenshot](samples/08_ambiguous_input/screenshot.png)

### 09 Conflict Handling

Proves: deterministic priority when one update contains multiple drift signals  
Notes: [notes](samples/09_conflict_handling/notes.md)  
Input: [input](samples/09_conflict_handling/input_updates.json)  
Parsed JSON: [structured output](samples/09_conflict_handling/structured_updates.json)  
Dashboard: [dashboard](samples/09_conflict_handling/dashboard.html)  
Screenshot: [screenshot](samples/09_conflict_handling/screenshot.png)

### 10 Malformed JSON

Proves: malformed input is rejected instead of guessed  
Notes: [notes](samples/10_malformed_json/notes.md)  
Bad input: [bad input](samples/10_malformed_json/bad_updates.json)  
Expected error: [expected error](samples/10_malformed_json/expected_error.txt)

## Reproduction Commands

Reproduce one sample:

```powershell
python governance_replay.py --input samples/03_authority_drift/input_updates.json --output-dir samples/03_authority_drift --full --no-open
```

Reproduce the pressure sample:

```powershell
python governance_replay.py --input samples/07_pressure_increase/baseline_input_updates.json --output-dir samples/07_pressure_increase --state-file samples/07_pressure_increase/last_run_state.json --no-open
python governance_replay.py --input samples/07_pressure_increase/input_updates.json --output-dir samples/07_pressure_increase --state-file samples/07_pressure_increase/last_run_state.json --no-open
```

## Reviewer Checklist

- [ ] Main script runs with `python governance_replay.py --full --no-open`
- [ ] Parsed JSON exists in `structured_updates.json`
- [ ] Rule snapshot exists in `rules_used.json`
- [ ] Dashboard exists as `dashboard.html`
- [ ] Screenshot exists as `screenshot.png`
- [ ] Drift classifications are visible per case
- [ ] Escalation calibration is visible per case
- [ ] Deterministic replay result is visible
- [ ] Pressure comparison is visible in sample `07_pressure_increase`
- [ ] Conflict handling is visible in sample `09_conflict_handling`
- [ ] Malformed JSON handling is visible in sample `10_malformed_json`
- [ ] Requirement-to-artifact proof is visible in `PROOF_MATRIX.md`
- [ ] Raw-to-parsed examples are visible in `PARSER_EXAMPLES.md`

## Known Limitations

- This is rule-based, not machine learning.
- It only detects wording covered by the configured keyword rules.
- Malformed JSON stops the run instead of guessing.
- It does not connect to a live production system by itself.
- Scheduling is expected to be handled externally by Task Scheduler, cron, or a similar scheduler.
- The sample stream generator is only for testing and demonstration.

## What Not To Overclaim

This project does not claim to be a full incident-management platform, security product, or universal log parser. It is a bounded prototype for making messy governance/operations updates structured, visible, deterministic, and reviewable.

## Final Reflection

The safest operational output is not the most fluent explanation. It is the one that can be replayed, inspected, challenged, and reproduced from visible rules.
