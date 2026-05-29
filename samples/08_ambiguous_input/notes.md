# 08 Ambiguous Input

Purpose: shows a 10-update batch where vague or mangled inputs are not guessed into fake safe decisions.

Input signal:

```text
Looking into it.
```

Expected result:

```text
target rows include ambiguous
operational_drift_classification = unclear/incomplete
recommended_action = request a clearer operational update
```

Reproduction command:

```powershell
python governance_replay.py --input samples/08_ambiguous_input/input_updates.json --output-dir samples/08_ambiguous_input --full --no-open
```
