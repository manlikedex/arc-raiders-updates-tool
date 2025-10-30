"""
PatchForge Core Module
======================

Shared logic for comparing Arc Raiders weapon data between patches.
Used by GUI, CLI, and automation tools.
"""

import json
import os
from typing import List, Dict, Tuple

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
METRICS = [
    ("bodyDamage", True),
    ("headDamage", True),
    ("fireRate", True),
    ("magSize", True),
    ("timeToKill", False),
    ("bodyDamageAfterFirstHit", True),
    ("headDamageAfterFirstHit", True),
]

THRESHOLDS = {
    "bodyDamage": (1, 5),
    "headDamage": (2, 8),
    "fireRate": (0.2, 1),
    "magSize": (1, 5),
    "timeToKill": (0.05, 0.2),
    "bodyDamageAfterFirstHit": (1, 5),
    "headDamageAfterFirstHit": (2, 8),
}


# ---------------------------------------------------------
# CORE UTILITIES
# ---------------------------------------------------------
def load_json(path: str) -> Dict:
    """Load a JSON file safely."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict, path: str):
    """Save JSON with indentation."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def severity(delta: float, key: str) -> str:
    """Return severity marker based on thresholds."""
    small, large = THRESHOLDS.get(key, (1, 5))
    if delta >= large:
        return "●"
    elif delta >= small:
        return "•"
    elif delta > 0:
        return "·"
    return ""


# ---------------------------------------------------------
# COMPARISON ENGINE
# ---------------------------------------------------------
def compare_jsons(old_data: dict, new_data: dict) -> List[Dict]:
    """
    Compare two weapon datasets.
    Returns a list of dicts for each stat comparison.
    """
    old_map = {w["name"]: w for w in old_data.get("weapons", [])}
    new_map = {w["name"]: w for w in new_data.get("weapons", [])}

    results = []

    for name in sorted(set(old_map.keys()) | set(new_map.keys())):
        old_stats = old_map.get(name, {}).get("stats", {})
        new_stats = new_map.get(name, {}).get("stats", {})

        for key, higher_better in METRICS:
            o = old_stats.get(key)
            n = new_stats.get(key)
            if (o is None) or (n is None):
                results.append({
                    "weapon": name,
                    "metric": key,
                    "old": o,
                    "new": n,
                    "delta": None,
                    "change": "Missing",
                    "status": "secondary"
                })
                continue

            delta = n - o
            abs_delta = abs(delta)

            if delta == 0:
                results.append({
                    "weapon": name,
                    "metric": key,
                    "old": o,
                    "new": n,
                    "delta": 0,
                    "change": "No Change",
                    "status": "secondary"
                })
            elif (higher_better and delta > 0) or (not higher_better and delta < 0):
                results.append({
                    "weapon": name,
                    "metric": key,
                    "old": o,
                    "new": n,
                    "delta": delta,
                    "change": f"Buff {severity(abs_delta, key)}",
                    "status": "success"
                })
            else:
                results.append({
                    "weapon": name,
                    "metric": key,
                    "old": o,
                    "new": n,
                    "delta": delta,
                    "change": f"Nerf {severity(abs_delta, key)}",
                    "status": "danger"
                })

    return results


# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------
def summarize_results(results: List[Dict]) -> Dict:
    """Aggregate patch statistics (counts, net deltas, etc.)."""
    summary = {
        "buffs": 0,
        "nerfs": 0,
        "nochange": 0,
        "mixed": 0,
        "totals": {},
    }

    weapon_states = {}
    for r in results:
        status = r["status"]
        if status == "success":
            summary["buffs"] += 1
            weapon_states.setdefault(r["weapon"], set()).add("buff")
        elif status == "danger":
            summary["nerfs"] += 1
            weapon_states.setdefault(r["weapon"], set()).add("nerf")
        elif status == "secondary":
            summary["nochange"] += 1

        metric = r["metric"]
        if isinstance(r["delta"], (int, float)):
            summary["totals"][metric] = summary["totals"].get(metric, 0) + r["delta"]

    summary["mixed"] = sum(1 for s in weapon_states.values() if "buff" in s and "nerf" in s)
    return summary
