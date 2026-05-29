import argparse
import json
import os
import random
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


SERVICES = [
    "Checkout",
    "Billing",
    "Payments",
    "Search",
    "Inventory",
    "Auth",
    "Orders",
]

ALIGNED_TEMPLATES = [
    "SERVICE is healthy. Trace attached. Approval granted. Replay matched. No escalation required.",
    "SERVICE stable. Evidence attached. Approval granted. Replay passed. No escalation required.",
]

RISK_TEMPLATES = [
    "SERVICE latency spike in production. No trace and no evidence attached. Escalated to service owner.",
    "SERVICE manual override completed without approval by unauthorized contractor. No escalation.",
    "SERVICE replay mismatch after rerun. Different result from the same input. Evidence attached. Escalated to team lead.",
    "SERVICE blocked by vendor API. Trace attached. Escalated to service owner.",
    "SERVICE owner missing during degraded release. Logs attached. Escalated to team lead.",
    "Looking into it.",
    "SERVICE stable. Evidence attached. Approval granted. Replay passed. Escalated to governance review.",
]


def positive_int(value):
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer greater than 0") from error

    if parsed < 1:
        raise argparse.ArgumentTypeError("must be an integer greater than 0")

    return parsed


def probability(value):
    try:
        parsed = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a number from 0 to 1") from error

    if parsed < 0 or parsed > 1:
        raise argparse.ArgumentTypeError("must be a number from 0 to 1")

    return parsed


def non_negative_float(value):
    try:
        parsed = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a number greater than or equal to 0") from error

    if parsed < 0:
        raise argparse.ArgumentTypeError("must be a number greater than or equal to 0")

    return parsed


def load_existing(path):
    if not path.exists() or path.stat().st_size == 0:
        return []

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("updates"), list):
        return data["updates"]
    raise SystemExit("stream file must be a JSON list or an object with updates")


def next_number(records):
    highest = 0
    for record in records:
        case_id = str(record.get("case_id") or record.get("update_id") or "")
        prefix, _, suffix = case_id.partition("-")
        if prefix in ("GOV", "UPD") and suffix.isdigit():
            highest = max(highest, int(suffix))
    return highest + 1


def utc_timestamp(offset_seconds):
    timestamp = datetime.now(timezone.utc) + timedelta(seconds=offset_seconds)
    return timestamp.isoformat(timespec="seconds").replace("+00:00", "Z")


def build_update(sequence, rng, drift_rate):
    service = rng.choice(SERVICES)
    templates = RISK_TEMPLATES if rng.random() < drift_rate else ALIGNED_TEMPLATES
    template = rng.choice(templates)
    return {
        "case_id": f"GOV-{sequence:03d}",
        "timestamp": utc_timestamp(sequence),
        "update": template.replace("SERVICE", service),
    }


def write_updates(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    with temporary_path.open("w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2, ensure_ascii=True)
        handle.write("\n")

    for attempt in range(5):
        try:
            temporary_path.replace(path)
            return
        except PermissionError as error:
            if attempt == 4:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass
                raise PermissionError(
                    f"Could not update {path}. Close the JSON file if it is open, "
                    "pause OneDrive sync if needed, or use a different --output file."
                ) from error
            time.sleep(0.25)


def main():
    parser = argparse.ArgumentParser(
        description="Generate raw governance updates for testing the replay system."
    )
    parser.add_argument("--output", default="input_updates.json", help="JSON output file.")
    parser.add_argument(
        "--count",
        "--max-events",
        "--max-updates",
        dest="count",
        type=positive_int,
        default=7,
        help="Number of updates to add.",
    )
    parser.add_argument("--reset", action="store_true", help="Replace the output file first.")
    parser.add_argument("--seed", type=int, default=None, help="Optional deterministic seed.")
    parser.add_argument("--quiet", action="store_true", help="Only print errors.")
    parser.add_argument(
        "--drift-rate",
        type=probability,
        default=0.65,
        help="Chance that a generated update contains governance drift.",
    )
    parser.add_argument(
        "--burst-chance",
        type=probability,
        default=0,
        help="Chance that one loop emits a burst of updates.",
    )
    parser.add_argument(
        "--max-burst-events",
        type=positive_int,
        default=5,
        help="Maximum events emitted in one burst.",
    )
    parser.add_argument(
        "--interval-seconds",
        type=non_negative_float,
        default=0,
        help="Pause between appended updates. Use 0 for immediate generation.",
    )
    parser.add_argument(
        "--jitter-seconds",
        type=non_negative_float,
        default=0,
        help="Add random delay up to this many seconds between updates.",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    rng = random.Random(args.seed)
    records = [] if args.reset else load_existing(output_path)
    sequence = next_number(records)

    emitted = 0
    while emitted < args.count:
        burst_size = 1
        if rng.random() < args.burst_chance:
            burst_size = rng.randint(1, args.max_burst_events)

        for _ in range(burst_size):
            if emitted >= args.count:
                break
            records.append(build_update(sequence, rng, args.drift_rate))
            sequence += 1
            emitted += 1

        write_updates(output_path, records)
        if args.interval_seconds > 0:
            delay = args.interval_seconds
            if args.jitter_seconds > 0:
                delay += rng.uniform(0, args.jitter_seconds)
            time.sleep(delay)

    if not args.quiet:
        print(f"Wrote {len(records)} total updates to {output_path}")


if __name__ == "__main__":
    main()
