from collections import defaultdict
from datetime import timedelta


def build_incidents(events):
    """
    Convert raw events → incidents
    """

    incidents = []

    # --- GROUP 1: Brute Force Detection (EventID 4625) ---
    failed_logons = [
        e for e in events if e["event_id"] == "4625"
    ]

    if len(failed_logons) >= 5:

        timestamps = [e["timestamp"] for e in failed_logons if e["timestamp"]]

        incidents.append({
            "title": "Possible Brute Force Attack",
            "severity": "high",
            "rule": "4625_Failure_Cluster",
            "event_count": len(failed_logons),
            "first_seen": min(timestamps) if timestamps else None,
            "last_seen": max(timestamps) if timestamps else None
        })

    # --- GROUP 2: Privilege escalation (4624 + 4672) ---
    priv_events = [
        e for e in events if e["event_id"] in ["4624", "4672"]
    ]

    if len(priv_events) >= 3:

        timestamps = [e["timestamp"] for e in priv_events if e["timestamp"]]

        incidents.append({
            "title": "Privilege Activity Detected",
            "severity": "medium",
            "rule": "Privilege_Escalation_Chain",
            "event_count": len(priv_events),
            "first_seen": min(timestamps) if timestamps else None,
            "last_seen": max(timestamps) if timestamps else None
        })

    # --- GROUP 3: Credential access patterns ---
    cred_events = [
        e for e in events if "Credential" in e["rule_title"]
    ]

    if len(cred_events) >= 3:

        timestamps = [e["timestamp"] for e in cred_events if e["timestamp"]]

        incidents.append({
            "title": "Credential Access Activity",
            "severity": "medium",
            "rule": "Credential_Manager_Activity",
            "event_count": len(cred_events),
            "first_seen": min(timestamps) if timestamps else None,
            "last_seen": max(timestamps) if timestamps else None
        })

    return incidents