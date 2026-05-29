import argparse
import csv
import hashlib
import html
import json
import shutil
import urllib.error
import urllib.request
import webbrowser
from datetime import datetime, timedelta, timezone
from pathlib import Path


DEFAULT_RULES = {
    "drift_priority": [
        "authority-drift",
        "replay-drift",
        "escalation-drift",
        "evidence-drift",
        "ownership-drift",
        "dependency-drift",
        "ambiguous",
        "aligned",
    ],
    "escalation_rank": [
        "none",
        "service-owner",
        "team-lead",
        "incident-commander",
        "governance-review",
    ],
    "keywords": {
        "status_failed": ["outage", "down", "failed", "failure", "critical"],
        "status_degraded": ["degraded", "slow", "latency", "error", "spike"],
        "status_blocked": ["blocked", "waiting", "stuck", "cannot proceed"],
        "status_healthy": ["healthy", "stable", "resolved", "normal"],
        "evidence_missing": [
            "missing trace",
            "no trace",
            "missing evidence",
            "no evidence",
            "no log",
            "no logs",
            "no metrics",
        ],
        "evidence_present": [
            "trace attached",
            "evidence attached",
            "logs attached",
            "metrics attached",
            "dashboard linked",
        ],
        "authority_risk": [
            "approval missing",
            "approval pending",
            "without approval",
            "unauthorized",
            "not authorized",
            "manual override",
            "bypassed approval",
        ],
        "authority_ok": ["approved", "approval granted", "authorized"],
        "replay_risk": [
            "replay mismatch",
            "rerun failed",
            "different result",
            "not reproducible",
            "cannot replay",
        ],
        "replay_ok": ["replay matched", "replay passed", "same result", "reproducible"],
        "dependency_risk": [
            "blocked by",
            "waiting on",
            "vendor",
            "database",
            "api",
            "queue",
            "integration",
        ],
        "owner_missing": ["no owner", "owner missing", "unassigned"],
        "impact_high": ["customer impact", "production", "prod", "data loss", "security"],
    },
    "expected_escalation_rules": [
        {
            "name": "authority_governance_review",
            "drift_any": ["authority-drift"],
            "expected": "governance-review",
        },
        {
            "name": "critical_incident_commander",
            "severity_any": ["critical"],
            "expected": "incident-commander",
        },
        {
            "name": "replay_team_lead",
            "drift_any": ["replay-drift"],
            "expected": "team-lead",
        },
        {
            "name": "evidence_team_lead",
            "drift_any": ["evidence-drift"],
            "expected": "team-lead",
        },
        {
            "name": "high_team_lead",
            "severity_any": ["high"],
            "expected": "team-lead",
        },
        {
            "name": "dependency_or_owner_service_owner",
            "drift_any": ["dependency-drift", "ownership-drift"],
            "expected": "service-owner",
        },
        {"name": "default", "expected": "none"},
    ],
}


def lower_text(value):
    return str(value or "").lower()


def has_any(text, keywords):
    return any(keyword in text for keyword in keywords)


def load_json(path):
    try:
        with Path(path).open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Could not read valid JSON from {path}: {exc}") from exc


def load_rules(path):
    if not path:
        return DEFAULT_RULES
    data = load_json(path)
    merged = json.loads(json.dumps(DEFAULT_RULES))
    for key, value in data.items():
        merged[key] = value
    return merged


def load_updates(path):
    data = load_json(path)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("updates", "cases", "events"):
            if isinstance(data.get(key), list):
                return data[key]
    raise SystemExit("Input must be a JSON list or an object with updates/cases/events.")


def fallback_timestamp(index):
    timestamp = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=index)
    return timestamp.isoformat(timespec="seconds").replace("+00:00", "Z")


def fetch_url_updates(url, limit_lines):
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            raw_text = response.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        raise SystemExit(f"Could not read input URL: {exc}") from exc

    updates = []
    for index, line in enumerate(raw_text.splitlines(), start=1):
        if limit_lines and len(updates) >= limit_lines:
            break
        text = line.strip()
        if not text:
            continue
        updates.append(
            {
                "case_id": f"URL-{len(updates) + 1:06d}",
                "timestamp": fallback_timestamp(len(updates) + 1),
                "update": text,
            }
        )
    return updates


def canonical_json(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(data):
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()[:16]


def present(value):
    return value not in (None, "", [])


def parse_timestamp(value):
    if not present(value):
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def raw_text_from_item(item):
    if isinstance(item, str):
        return item
    if not isinstance(item, dict):
        return str(item)

    for key in ("update", "text", "message", "raw_update"):
        if item.get(key):
            return str(item[key])

    parts = []
    for key in (
        "classification",
        "action",
        "owner",
        "approval_status",
        "trace_id",
        "evidence_id",
        "replay_expected_action",
    ):
        if item.get(key) not in (None, ""):
            parts.append(f"{key}: {item[key]}")
    return ". ".join(parts)


def normalize_escalation(value):
    text = lower_text(value).replace("_", "-")
    if not text or text == "unknown":
        return "not-visible"
    if "governance" in text:
        return "governance-review"
    if "incident" in text or "commander" in text:
        return "incident-commander"
    if "team" in text or "lead" in text or "manager" in text:
        return "team-lead"
    if "service" in text or "owner" in text:
        return "service-owner"
    if "none" in text or "no escalation" in text or "not escalated" in text:
        return "none"
    return text


def extract_actual_escalation(raw_text, item):
    if isinstance(item, dict) and item.get("actual_escalation"):
        return normalize_escalation(item.get("actual_escalation"))

    text = lower_text(raw_text)
    if "no escalation" in text or "not escalated" in text:
        return "none"
    if "escalated to governance" in text or "governance review" in text:
        return "governance-review"
    if "escalated to incident" in text or "incident commander" in text:
        return "incident-commander"
    if "escalated to team" in text or "team lead" in text or "manager" in text:
        return "team-lead"
    if "escalated to service" in text or "service owner" in text:
        return "service-owner"
    return "not-visible"


def extract_system_status(text, keywords):
    if has_any(text, keywords["status_failed"]):
        return "failed"
    if has_any(text, keywords["status_degraded"]):
        return "degraded"
    if has_any(text, keywords["status_blocked"]):
        return "blocked"
    if has_any(text, keywords["status_healthy"]):
        return "healthy"
    return "unknown"


def extract_service(raw_text, item):
    if isinstance(item, dict) and item.get("service"):
        return str(item["service"])
    text = lower_text(raw_text)
    known_services = [
        "checkout",
        "billing",
        "payments",
        "search",
        "inventory",
        "auth",
        "database",
        "queue",
        "orders",
    ]
    for service in known_services:
        if service in text:
            return service
    return "unknown"


def extract_matches(text, keywords):
    return [keyword for keyword in keywords if keyword in text]


def legacy_classification(primary_drift):
    mapping = {
        "aligned": "aligned",
        "authority-drift": "authority-risk",
        "replay-drift": "replay-risk",
        "escalation-drift": "authority-risk",
        "evidence-drift": "observability-risk",
        "ownership-drift": "integration-risk",
        "dependency-drift": "integration-risk",
        "ambiguous": "unclear/incomplete",
    }
    return mapping.get(primary_drift, "unclear/incomplete")


def structured_status_from_item(item, current_status):
    if not isinstance(item, dict):
        return current_status

    classification = lower_text(item.get("classification"))
    if classification in ("critical", "sev1", "sev-1", "failed", "outage"):
        return "failed"
    if classification in ("warning", "degraded", "medium", "high"):
        return "degraded"
    if classification in ("healthy", "stable", "normal", "ok"):
        return "healthy"
    return current_status


def detect_severity(text, drift_types, status, keywords):
    if status == "failed" or has_any(text, keywords["impact_high"]):
        return "critical"
    if "authority-drift" in drift_types or "replay-drift" in drift_types:
        return "high"
    if status == "degraded" or "evidence-drift" in drift_types:
        return "high"
    if status == "blocked" or "dependency-drift" in drift_types:
        return "medium"
    if status == "healthy" and drift_types == ["aligned"]:
        return "low"
    return "medium"


def classify_primary(drift_types, priority):
    drift_set = set(drift_types)
    for label in priority:
        if label in drift_set:
            return label
    return "aligned"


def choose_expected_escalation(drift_types, severity, rules):
    drift_set = set(drift_types)
    for rule in rules.get("expected_escalation_rules", []):
        if rule.get("name") == "default":
            continue
        matches = True
        if "drift_any" in rule:
            matches = matches and bool(drift_set.intersection(rule["drift_any"]))
        if "severity_any" in rule:
            matches = matches and severity in rule["severity_any"]
        if matches:
            return rule["expected"], rule.get("name", "matched_rule")

    for rule in rules.get("expected_escalation_rules", []):
        if rule.get("name") == "default":
            return rule["expected"], "default"
    return "none", "default"


def compare_escalation(expected, actual, escalation_rank):
    if actual == "not-visible":
        if expected == "none":
            return "calibrated", "no escalation was expected and none was visible"
        return "under-escalated", "required escalation was not visible"

    rank = {name: index for index, name in enumerate(escalation_rank)}
    expected_rank = rank.get(expected, 0)
    actual_rank = rank.get(actual, 0)

    if actual_rank == expected_rank:
        return "calibrated", "actual escalation matched expected escalation"
    if actual_rank < expected_rank:
        return "under-escalated", "actual escalation was lower than expected"
    return "over-escalated", "actual escalation was higher than expected"


def parse_update(item, index, rules):
    if isinstance(item, str):
        raw_text = raw_text_from_item(item)
        case_id = f"CASE-{index:03d}"
        timestamp = ""
    elif isinstance(item, dict):
        raw_text = raw_text_from_item(item)
        case_id = item.get("case_id") or item.get("update_id") or item.get("event_id") or f"CASE-{index:03d}"
        timestamp = item.get("timestamp", "")
    else:
        raw_text = raw_text_from_item(item)
        case_id = f"CASE-{index:03d}"
        timestamp = ""

    text = lower_text(raw_text)
    keywords = rules["keywords"]

    service = extract_service(raw_text, item)
    system_status = structured_status_from_item(item, extract_system_status(text, keywords))

    evidence_state = "unknown"
    if has_any(text, keywords["evidence_missing"]):
        evidence_state = "missing"
    elif has_any(text, keywords["evidence_present"]):
        evidence_state = "present"
    elif isinstance(item, dict) and (item.get("trace_id") or item.get("evidence_id")):
        evidence_state = "present"

    approval_state = "unknown"
    if isinstance(item, dict) and item.get("approval_required") is False:
        approval_state = "not-required"
    elif isinstance(item, dict) and lower_text(item.get("approval_status")) in ("approved", "granted"):
        approval_state = "approved"
    elif isinstance(item, dict) and lower_text(item.get("approval_status")) in ("pending", "missing", "not approved"):
        approval_state = "unsafe"
    elif "no approval required" in text or "approval was not required" in text:
        approval_state = "not-required"
    elif has_any(text, keywords["authority_risk"]):
        approval_state = "unsafe"
    elif has_any(text, keywords["authority_ok"]):
        approval_state = "approved"

    actor_authorized = "unknown"
    if isinstance(item, dict) and item.get("authorized_actor") is False:
        actor_authorized = "no"
    elif isinstance(item, dict) and item.get("authorized_actor") is True:
        actor_authorized = "yes"
    elif "unauthorized" in text or "not authorized" in text:
        actor_authorized = "no"
    elif "authorized" in text:
        actor_authorized = "yes"

    replay_state = "unknown"
    if (
        isinstance(item, dict)
        and item.get("replay_expected_action")
        and item.get("action")
        and item.get("replay_expected_action") != item.get("action")
    ):
        replay_state = "mismatch"
    elif (
        isinstance(item, dict)
        and item.get("replay_expected_action")
        and item.get("action")
        and item.get("replay_expected_action") == item.get("action")
    ):
        replay_state = "matched"
    elif has_any(text, keywords["replay_risk"]):
        replay_state = "mismatch"
    elif has_any(text, keywords["replay_ok"]):
        replay_state = "matched"

    owner_state = "visible"
    if isinstance(item, dict) and item.get("owner") in (None, "") and (
        item.get("classification") or item.get("action")
    ):
        owner_state = "missing"
    elif has_any(text, keywords["owner_missing"]):
        owner_state = "missing"

    dependency_state = "clear"
    if has_any(text, keywords["dependency_risk"]):
        dependency_state = "blocked"

    drift_types = []
    if approval_state == "unsafe" or actor_authorized == "no":
        drift_types.append("authority-drift")
    if replay_state == "mismatch":
        drift_types.append("replay-drift")
    if evidence_state == "missing":
        drift_types.append("evidence-drift")
    if owner_state == "missing":
        drift_types.append("ownership-drift")
    if dependency_state == "blocked":
        drift_types.append("dependency-drift")
    if len(text.split()) < 4 or system_status == "unknown" and not drift_types:
        drift_types.append("ambiguous")
    if not drift_types:
        drift_types.append("aligned")

    severity = detect_severity(text, drift_types, system_status, keywords)
    expected_escalation, escalation_rule = choose_expected_escalation(drift_types, severity, rules)
    actual_escalation = extract_actual_escalation(raw_text, item)
    calibration, calibration_reason = compare_escalation(
        expected_escalation,
        actual_escalation,
        rules["escalation_rank"],
    )

    if calibration in ("under-escalated", "over-escalated") and "escalation-drift" not in drift_types:
        drift_types.append("escalation-drift")
    if len(drift_types) > 1 and "aligned" in drift_types:
        drift_types = [drift for drift in drift_types if drift != "aligned"]

    primary_drift = classify_primary(drift_types, rules["drift_priority"])
    secondary_drifts = [drift for drift in drift_types if drift != primary_drift]
    conflict_detected = bool(secondary_drifts)
    if conflict_detected:
        conflict_resolution = (
            f"{primary_drift} selected by drift_priority over "
            f"{', '.join(secondary_drifts)}"
        )
    else:
        conflict_resolution = "single drift label"
    operational_classification = legacy_classification(primary_drift)
    blockers = extract_matches(text, keywords["status_blocked"])
    dependencies = extract_matches(text, keywords["dependency_risk"])
    replay_risks = extract_matches(text, keywords["replay_risk"])
    observability_risks = extract_matches(text, keywords["evidence_missing"])
    governance_risks = extract_matches(text, keywords["authority_risk"])

    checks = {
        "structured": bool(case_id and raw_text and timestamp and system_status != "unknown"),
        "observable": evidence_state == "present",
        "deterministic": replay_state != "mismatch",
        "governance_safe": (
            approval_state in ("approved", "not-required", "unknown")
            and actor_authorized != "no"
            and calibration == "calibrated"
        ),
    }

    if primary_drift == "authority-drift":
        action = "hold execution until approval and authorization are visible"
    elif primary_drift == "replay-drift":
        action = "rerun replay before treating the decision as stable"
    elif primary_drift == "escalation-drift":
        action = "correct escalation level before continuing"
    elif primary_drift == "evidence-drift":
        action = "attach trace, logs, or evidence before review"
    elif primary_drift == "ownership-drift":
        action = "assign an owner before execution continues"
    elif primary_drift == "dependency-drift":
        action = "resolve dependency blocker or escalate to service owner"
    elif primary_drift == "ambiguous":
        action = "request a clearer operational update"
    else:
        action = "continue with normal monitoring"

    result = {
        "case_id": str(case_id),
        "timestamp": timestamp,
        "raw_update": raw_text,
        "service": service,
        "system_status": system_status,
        "blockers": blockers,
        "dependencies": dependencies,
        "replay_risks": replay_risks,
        "observability_risks": observability_risks,
        "governance_risks": governance_risks,
        "severity": severity,
        "evidence_state": evidence_state,
        "approval_state": approval_state,
        "actor_authorized": actor_authorized,
        "replay_state": replay_state,
        "owner_state": owner_state,
        "dependency_state": dependency_state,
        "drift_types": drift_types,
        "primary_drift": primary_drift,
        "secondary_drifts": secondary_drifts,
        "conflict_detected": conflict_detected,
        "conflict_resolution": conflict_resolution,
        "operational_drift_classification": operational_classification,
        "expected_escalation": expected_escalation,
        "actual_escalation": actual_escalation,
        "escalation_rule": escalation_rule,
        "calibration": calibration,
        "calibration_reason": calibration_reason,
        "checks": checks,
        "safe_to_continue": all(checks.values()),
        "recommended_action": action,
    }
    result["replay_hash"] = stable_hash(result)
    return result


def evaluate_updates(updates, rules):
    return [parse_update(item, index, rules) for index, item in enumerate(updates, start=1)]


def summarize(cases, deterministic_replay_pass):
    drift_counts = {}
    operational_drift_counts = {}
    calibration_counts = {}
    check_counts = {
        "structured": 0,
        "observable": 0,
        "deterministic": 0,
        "governance_safe": 0,
    }

    for case in cases:
        drift_counts[case["primary_drift"]] = drift_counts.get(case["primary_drift"], 0) + 1
        legacy_name = case["operational_drift_classification"]
        operational_drift_counts[legacy_name] = operational_drift_counts.get(legacy_name, 0) + 1
        calibration_counts[case["calibration"]] = calibration_counts.get(case["calibration"], 0) + 1
        for key in check_counts:
            if case["checks"][key]:
                check_counts[key] += 1

    total = len(cases)
    metric_rates = {}
    for key, value in check_counts.items():
        metric_rates[key] = round((value / total) * 100, 2) if total else 0.0

    return {
        "total_cases": total,
        "deterministic_replay_pass": deterministic_replay_pass,
        "drift_counts": drift_counts,
        "operational_drift_counts": operational_drift_counts,
        "calibration_counts": calibration_counts,
        "metric_rates": metric_rates,
        "unsafe_cases": [
            case["case_id"] for case in cases if not case["safe_to_continue"]
        ],
    }


def load_previous_state(path):
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        return None


def max_timestamp(records):
    latest = None
    for record in records:
        if isinstance(record, dict):
            timestamp = parse_timestamp(record.get("timestamp"))
            if timestamp and (latest is None or timestamp > latest):
                latest = timestamp
    return latest.isoformat().replace("+00:00", "Z") if latest else None


def select_updates_for_run(updates, previous_state, full=False, state_enabled=True):
    if full or not state_enabled or not previous_state or not previous_state.get("last_timestamp"):
        return updates

    previous_timestamp = parse_timestamp(previous_state.get("last_timestamp"))
    if not previous_timestamp:
        return updates

    selected = []
    for update in updates:
        if not isinstance(update, dict):
            selected.append(update)
            continue

        timestamp = parse_timestamp(update.get("timestamp"))
        if timestamp is None or timestamp > previous_timestamp:
            selected.append(update)

    return selected


def compare_pressure(summary, state_path, previous=None, enabled=True):
    current_snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_cases": summary["total_cases"],
        "metric_rates": summary["metric_rates"],
        "drift_counts": summary["drift_counts"],
        "operational_drift_counts": summary["operational_drift_counts"],
        "calibration_counts": summary["calibration_counts"],
    }

    if not enabled:
        return {
            "enabled": False,
            "state_file": str(state_path),
            "pressure_direction": "not-tracked",
            "stable_under_pressure": None,
            "metric_deltas": {},
            "note": "state tracking disabled for this run",
        }, current_snapshot

    if previous is None:
        previous = load_previous_state(state_path)

    if not previous:
        return {
            "enabled": True,
            "state_file": str(state_path),
            "previous_total_cases": None,
            "current_total_cases": summary["total_cases"],
            "pressure_direction": "baseline",
            "stable_under_pressure": None,
            "metric_deltas": {},
            "note": "no previous run found; this run becomes the baseline",
        }, current_snapshot

    previous_total = previous.get("total_cases", 0)
    current_total = summary["total_cases"]
    if current_total > previous_total:
        direction = "increased"
    elif current_total < previous_total:
        direction = "decreased"
    else:
        direction = "same"

    previous_rates = previous.get("metric_rates", {})
    metric_deltas = {}
    for name, current_value in summary["metric_rates"].items():
        previous_value = previous_rates.get(name)
        metric_deltas[name] = (
            None if previous_value is None else round(current_value - previous_value, 2)
        )

    if direction == "increased":
        stable_under_pressure = all(
            value is not None and value >= 0 for value in metric_deltas.values()
        )
        note = "pressure increased; metric deltas show whether intelligence stayed stable"
    else:
        stable_under_pressure = None
        note = "pressure did not increase; stability-under-pressure is not judged"

    return {
        "enabled": True,
        "state_file": str(state_path),
        "previous_total_cases": previous_total,
        "current_total_cases": current_total,
        "pressure_direction": direction,
        "stable_under_pressure": stable_under_pressure,
        "metric_deltas": metric_deltas,
        "note": note,
    }, current_snapshot


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=True)
        handle.write("\n")


def write_csv(path, cases):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "case_id",
        "service",
        "system_status",
        "severity",
        "primary_drift",
        "secondary_drifts",
        "conflict_detected",
        "conflict_resolution",
        "operational_drift_classification",
        "drift_types",
        "expected_escalation",
        "actual_escalation",
        "calibration",
        "structured",
        "observable",
        "deterministic",
        "governance_safe",
        "safe_to_continue",
        "recommended_action",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for case in cases:
            writer.writerow(
                {
                    "case_id": case["case_id"],
                    "service": case["service"],
                    "system_status": case["system_status"],
                    "severity": case["severity"],
                    "primary_drift": case["primary_drift"],
                    "secondary_drifts": "; ".join(case["secondary_drifts"]),
                    "conflict_detected": case["conflict_detected"],
                    "conflict_resolution": case["conflict_resolution"],
                    "operational_drift_classification": case["operational_drift_classification"],
                    "drift_types": "; ".join(case["drift_types"]),
                    "expected_escalation": case["expected_escalation"],
                    "actual_escalation": case["actual_escalation"],
                    "calibration": case["calibration"],
                    "structured": case["checks"]["structured"],
                    "observable": case["checks"]["observable"],
                    "deterministic": case["checks"]["deterministic"],
                    "governance_safe": case["checks"]["governance_safe"],
                    "safe_to_continue": case["safe_to_continue"],
                    "recommended_action": case["recommended_action"],
                }
            )


def check_state(value):
    return "pass" if value else "fail"


def format_delta(value):
    if value is None:
        return "n/a"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}"


def observed_drift_summary(summary):
    display_names = {
        "authority-drift": "authority drift",
        "evidence-drift": "missing evidence",
        "replay-drift": "replay mismatch",
        "escalation-drift": "escalation drift",
        "dependency-drift": "dependency drift",
        "ownership-drift": "ownership drift",
        "ambiguous": "ambiguous input",
        "aligned": "aligned",
    }
    order = [
        "authority-drift",
        "evidence-drift",
        "replay-drift",
        "escalation-drift",
        "dependency-drift",
        "ownership-drift",
        "ambiguous",
        "aligned",
    ]
    counts = summary.get("drift_counts", {})
    parts = []

    for name in order:
        count = counts.get(name, 0)
        if count:
            label = display_names.get(name, name)
            parts.append(f"{label} ({count})")

    return ", ".join(parts) if parts else "none"


def write_dashboard(path, cases, summary, pressure):
    path.parent.mkdir(parents=True, exist_ok=True)
    css_source = Path(__file__).with_name("dashboard.css")
    css_target = path.parent / "dashboard.css"
    if css_source.exists() and css_source.resolve() != css_target.resolve():
        shutil.copyfile(css_source, css_target)

    metric_cards = "\n".join(
        f"""
        <section class="metric-card">
          <span>{html.escape(name.replace("_", " ").title())}</span>
          <strong>{rate:.2f}%</strong>
        </section>
        """
        for name, rate in summary["metric_rates"].items()
    )

    drift_rows = "\n".join(
        f"<tr><td>{html.escape(name)}</td><td>{count}</td></tr>"
        for name, count in sorted(summary["drift_counts"].items())
    )

    operational_drift_rows = "\n".join(
        f"<tr><td>{html.escape(name)}</td><td>{count}</td></tr>"
        for name, count in sorted(summary["operational_drift_counts"].items())
    )

    calibration_rows = "\n".join(
        f"<tr><td>{html.escape(name)}</td><td>{count}</td></tr>"
        for name, count in sorted(summary["calibration_counts"].items())
    )

    pressure_rows = "\n".join(
        f"<tr><td>{html.escape(name.replace('_', ' '))}</td><td>{format_delta(value)}</td></tr>"
        for name, value in pressure.get("metric_deltas", {}).items()
    )
    if not pressure_rows:
        pressure_rows = "<tr><td colspan=\"2\">No previous run to compare.</td></tr>"

    case_rows = []
    for case in cases:
        checks = " ".join(
            f"<span class=\"check\" data-state=\"{check_state(value)}\">{html.escape(name)}</span>"
            for name, value in case["checks"].items()
        )
        case_rows.append(
            f"""
            <tr>
              <td>{html.escape(case["case_id"])}</td>
              <td>{html.escape(case["service"])}</td>
              <td>{html.escape(case["system_status"])}</td>
              <td>{html.escape(case["primary_drift"])}</td>
              <td class="compact-text">{html.escape(', '.join(case["drift_types"]))}</td>
              <td class="compact-text">{html.escape(case["conflict_resolution"])}</td>
              <td>{html.escape(case["operational_drift_classification"])}</td>
              <td>{html.escape(case["expected_escalation"])}</td>
              <td>{html.escape(case["actual_escalation"])}</td>
              <td>{html.escape(case["calibration"])}</td>
              <td>{checks}</td>
              <td>{html.escape(case["recommended_action"])}</td>
            </tr>
            """
        )

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Governance Drift Replay Dashboard</title>
  <link rel="stylesheet" href="dashboard.css">
</head>
<body>
  <main class="page">
    <header class="topbar">
      <div>
        <p class="eyebrow">Governance SHAKTI - 7-4-3 Test 3 Final</p>
        <h1>Governance Drift Replay Dashboard</h1>
      </div>
      <div class="status-pill">Replay deterministic: {str(summary["deterministic_replay_pass"]).lower()}</div>
    </header>

    <section class="summary-grid">
      <section class="summary-card">
        <h2>Run Summary</h2>
        <p><strong>Total cases:</strong> {summary["total_cases"]}</p>
        <p><strong>Unsafe cases:</strong> {html.escape(", ".join(summary["unsafe_cases"]) or "none")}</p>
        <p><strong>Observed drift:</strong> {html.escape(observed_drift_summary(summary))}</p>
      </section>
      <section class="summary-card">
        <h2>Pressure Comparison</h2>
        <p><strong>Direction:</strong> {html.escape(str(pressure.get("pressure_direction")))}</p>
        <p><strong>Previous cases:</strong> {html.escape(str(pressure.get("previous_total_cases", "n/a")))}</p>
        <p><strong>Current cases:</strong> {html.escape(str(pressure.get("current_total_cases", summary["total_cases"])))}</p>
        <p><strong>Stable under pressure:</strong> {html.escape(str(pressure.get("stable_under_pressure")))}</p>
      </section>
    </section>

    <section class="metrics">
      {metric_cards}
    </section>

    <section class="tables">
      <section>
        <h2>Governance Drift Counts</h2>
        <table>
          <thead><tr><th>Primary drift</th><th>Count</th></tr></thead>
          <tbody>{drift_rows}</tbody>
        </table>
      </section>
      <section>
        <h2>Operational Drift Taxonomy</h2>
        <table>
          <thead><tr><th>Classification</th><th>Count</th></tr></thead>
          <tbody>{operational_drift_rows}</tbody>
        </table>
      </section>
      <section>
        <h2>Escalation Calibration</h2>
        <table>
          <thead><tr><th>Calibration</th><th>Count</th></tr></thead>
          <tbody>{calibration_rows}</tbody>
        </table>
      </section>
      <section>
        <h2>Metric Delta From Previous Run</h2>
        <table>
          <thead><tr><th>Metric</th><th>Delta</th></tr></thead>
          <tbody>{pressure_rows}</tbody>
        </table>
      </section>
    </section>

    <section class="case-section">
      <h2>Case Replay Results</h2>
      <table class="case-table">
        <thead>
          <tr>
            <th>Case</th>
            <th>Service</th>
            <th>Status</th>
            <th>Governance Drift</th>
            <th>All Drift Labels</th>
            <th>Conflict Handling</th>
            <th>Operational Drift</th>
            <th>Expected</th>
            <th>Actual</th>
            <th>Calibration</th>
            <th>Checks</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>{"".join(case_rows)}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""
    path.write_text(html_text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Replay messy governance updates and calibrate escalation decisions."
    )
    parser.add_argument(
        "--input",
        default="samples/00_default_example/input_updates.json",
        help="Input JSON file.",
    )
    parser.add_argument("--input-url", default=None, help="Read raw text updates from a URL.")
    parser.add_argument(
        "--limit-lines",
        type=int,
        default=300,
        help="Maximum raw URL lines to read when --input-url is used.",
    )
    parser.add_argument("--rules", default="escalation_rules.json", help="Rules JSON file.")
    parser.add_argument("--output-dir", default="outputs", help="Output directory.")
    parser.add_argument("--dashboard", default="dashboard.html", help="Dashboard HTML filename.")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Analyze the full input as a demo run instead of only new stateful records.",
    )
    parser.add_argument(
        "--state-file",
        default=None,
        help="State file used for pressure comparison. Default: output-dir/last_run_state.json",
    )
    parser.add_argument(
        "--no-state",
        action="store_true",
        help="Disable previous-run pressure comparison and state update.",
    )
    parser.add_argument("--open", action="store_true", help="Open the dashboard after writing it.")
    parser.add_argument("--no-open", action="store_true", help="Do not open the dashboard.")
    args = parser.parse_args()

    input_path = Path(args.input)
    rules_path = Path(args.rules)
    output_dir = Path(args.output_dir)
    state_path = Path(args.state_file) if args.state_file else output_dir / "last_run_state.json"
    state_enabled = not args.no_state and not args.full

    rules = load_rules(rules_path if rules_path.exists() else None)
    updates = fetch_url_updates(args.input_url, args.limit_lines) if args.input_url else load_updates(input_path)
    previous_state = load_previous_state(state_path) if state_enabled else None
    updates_for_run = select_updates_for_run(
        updates,
        previous_state,
        full=args.full,
        state_enabled=state_enabled,
    )

    first_pass = evaluate_updates(updates_for_run, rules)
    second_pass = evaluate_updates(updates_for_run, rules)
    deterministic_replay_pass = canonical_json(first_pass) == canonical_json(second_pass)
    summary = summarize(first_pass, deterministic_replay_pass)
    pressure, state_snapshot = compare_pressure(
        summary,
        state_path,
        previous=previous_state,
        enabled=state_enabled,
    )
    state_snapshot["last_timestamp"] = max_timestamp(updates) or (
        previous_state or {}
    ).get("last_timestamp")

    run_result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_file": args.input_url or str(input_path),
        "rules_file": str(rules_path if rules_path.exists() else "built-in defaults"),
        "mode": "full" if args.full else "stateful",
        "total_input_records": len(updates),
        "analyzed_records": len(updates_for_run),
        "summary": summary,
        "pressure_comparison": pressure,
        "cases": first_pass,
    }

    write_json(output_dir / "structured_updates.json", first_pass)
    write_json(output_dir / "replay_results.json", run_result)
    write_json(output_dir / "pressure_comparison.json", pressure)
    write_json(
        output_dir / "rules_used.json",
        {
            "rules_file": str(rules_path if rules_path.exists() else "built-in defaults"),
            "rules": rules,
        },
    )
    if state_enabled:
        write_json(state_path, state_snapshot)
    write_csv(output_dir / "escalation_report.csv", first_pass)
    dashboard_path = output_dir / args.dashboard
    write_dashboard(dashboard_path, first_pass, summary, pressure)

    print("Governance replay complete")
    print(f"- structured output: {output_dir / 'structured_updates.json'}")
    print(f"- replay output:     {output_dir / 'replay_results.json'}")
    print(f"- pressure output:   {output_dir / 'pressure_comparison.json'}")
    print(f"- rules used:        {output_dir / 'rules_used.json'}")
    print(f"- csv report:        {output_dir / 'escalation_report.csv'}")
    print(f"- dashboard:         {dashboard_path}")
    print(f"- deterministic replay pass: {deterministic_replay_pass}")
    print(f"- analyzed records: {len(updates_for_run)} of {len(updates)}")

    should_open = args.open or (args.full and not args.no_open)
    if should_open:
        webbrowser.open(dashboard_path.resolve().as_uri())


if __name__ == "__main__":
    main()
