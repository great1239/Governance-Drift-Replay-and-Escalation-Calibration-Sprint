# Rule Configuration

The program is intentionally rule-based. The active machine-readable config is:

```text
escalation_rules.json
```

Every run also writes the loaded config to:

```text
outputs/rules_used.json
```

The saved samples include the same file inside each sample folder.

## Drift Priority

When one update has multiple drift signals, the program keeps all matching labels but chooses one primary label using this order:

1. `authority-drift`
2. `replay-drift`
3. `escalation-drift`
4. `evidence-drift`
5. `ownership-drift`
6. `dependency-drift`
7. `ambiguous`
8. `aligned`

This is what handles edge-case conflicts.

## Escalation Rank

Escalation levels are ordered from lowest to highest:

1. `none`
2. `service-owner`
3. `team-lead`
4. `incident-commander`
5. `governance-review`

The program compares expected escalation against actual escalation using this order.

## Expected Escalation Rules

- `authority-drift` expects `governance-review`
- `critical` severity expects `incident-commander`
- `replay-drift` expects `team-lead`
- `evidence-drift` expects `team-lead`
- `high` severity expects `team-lead`
- `dependency-drift` or `ownership-drift` expects `service-owner`
- otherwise expected escalation is `none`

## Keyword Groups

The keyword groups in `escalation_rules.json` are used to detect:

- failed status
- degraded status
- blocked status
- healthy status
- missing evidence
- present evidence
- authority risk
- authority OK
- replay risk
- replay OK
- dependency risk
- missing owner
- high impact

This keeps the parser deterministic and easy to inspect.
