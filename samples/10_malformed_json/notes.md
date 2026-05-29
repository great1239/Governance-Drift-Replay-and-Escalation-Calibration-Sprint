# 10 Malformed JSON

Purpose: proves the program stops on malformed JSON instead of guessing or silently producing a misleading dashboard.

This is a failure-only sample. It intentionally does not include generated dashboard/CSV/JSON outputs because the expected behavior is to reject the bad input.

Reproduction command:

```powershell
python governance_replay.py --input samples/10_malformed_json/bad_updates.json --full --no-open
```

Expected result:

```text
Could not read valid JSON from samples\10_malformed_json\bad_updates.json: Expecting ',' delimiter: line 10 column 5 (char 210)
```

Saved proof:
[expected_error.txt](expected_error.txt)
