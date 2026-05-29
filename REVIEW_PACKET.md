# Review Packet

Use this file as the inspection order. It points to artifacts first.

## Start Here

Inspection log:
[INSPECTION_LOG.md](INSPECTION_LOG.md)

Requirement proof matrix:
[PROOF_MATRIX.md](PROOF_MATRIX.md)

Raw-to-parsed examples:
[PARSER_EXAMPLES.md](PARSER_EXAMPLES.md)

Default dashboard:
[samples/00_default_example/dashboard.html](samples/00_default_example/dashboard.html)

Default screenshot:
[samples/00_default_example/screenshot.png](samples/00_default_example/screenshot.png)

## Run Commands

Default run:

```powershell
python governance_replay.py --full --no-open
```

Custom input:

```powershell
python governance_replay.py --input your_updates.json --full --no-open
```

Stateful run:

```powershell
python governance_replay.py --input samples/00_default_example/input_updates.json
```

Malformed JSON proof:

```powershell
python governance_replay.py --input samples/10_malformed_json/bad_updates.json --full --no-open
```

## Files To Inspect

Main program:
[governance_replay.py](governance_replay.py)

Rule explanation:
[RULES.md](RULES.md)

Rule config:
[escalation_rules.json](escalation_rules.json)

Sample index:
[samples/README.md](samples/README.md)

## Output Files

Runtime output folder:
`outputs/`

Expected runtime files:

```text
structured_updates.json
replay_results.json
pressure_comparison.json
rules_used.json
escalation_report.csv
dashboard.html
dashboard.css
```

Curated proof outputs:
[samples/](samples/)

## Evidence Cases

Default run:
[samples/00_default_example](samples/00_default_example)

Aligned behavior:
[samples/01_aligned](samples/01_aligned)

Missing evidence:
[samples/02_missing_evidence](samples/02_missing_evidence)

Authority drift:
[samples/03_authority_drift](samples/03_authority_drift)

Replay mismatch:
[samples/04_replay_mismatch](samples/04_replay_mismatch)

Under-escalated:
[samples/05_under_escalated](samples/05_under_escalated)

Over-escalated:
[samples/06_over_escalated](samples/06_over_escalated)

Pressure increase:
[samples/07_pressure_increase](samples/07_pressure_increase)

Ambiguous input:
[samples/08_ambiguous_input](samples/08_ambiguous_input)

Conflict handling:
[samples/09_conflict_handling](samples/09_conflict_handling)

Malformed JSON:
[samples/10_malformed_json](samples/10_malformed_json)

## Checklist

- [ ] `python governance_replay.py --full --no-open` runs
- [ ] `outputs/structured_updates.json` is generated
- [ ] `outputs/rules_used.json` is generated
- [ ] dashboard HTML is generated
- [ ] sample screenshots are full-page
- [ ] `PROOF_MATRIX.md` maps requirements to files and fields
- [ ] `PARSER_EXAMPLES.md` shows raw-to-structured conversion
- [ ] `samples/07_pressure_increase/pressure_comparison.json` shows pressure comparison
- [ ] `samples/09_conflict_handling/structured_updates.json` shows conflict resolution
- [ ] `samples/10_malformed_json/expected_error.txt` shows failure behavior

## Limits

- Rule-based parser.
- No live system connection.
- No scheduler built in.
- Bad JSON fails instead of being repaired.
- Test stream generator is only for demos.
