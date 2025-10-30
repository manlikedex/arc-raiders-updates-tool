"""
PatchForge CLI — Arc Raiders Patch Comparison Tool
===================================================
Use PatchForge from the command line.

Examples:
    python patchforge_cli.py compare old.json new.json --export summary.html
    python patchforge_cli.py summary old.json new.json
    python patchforge_cli.py compare old.json new.json --csv patch_diff.csv
"""

import argparse
import json
import os
import sys
from datetime import datetime

from patchforge_core import load_json, compare_jsons, summarize_results


# ---------------------------------------------------------
# Export Utilities
# ---------------------------------------------------------
def export_csv(results, path):
    import csv
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Weapon", "Metric", "Old", "New", "Δ", "Change"])
        for r in results:
            delta_str = "–" if r["delta"] is None else f"{r['delta']:+.2f}"
            writer.writerow([
                r["weapon"], r["metric"], r["old"], r["new"], delta_str, r["change"]
            ])
    print(f"✅ CSV exported: {path}")


def export_html(results, path):
    rows = []
    for r in results:
        color = {
            "success": "#6fdc8c",
            "danger": "#f28b82",
            "warning": "#fdd388",
            "secondary": "#cccccc"
        }.get(r["status"], "white")
        delta_str = "–" if r["delta"] is None else f"{r['delta']:+.2f}"
        rows.append(
            f"<tr style='color:{color}'><td>{r['weapon']}</td>"
            f"<td>{r['metric']}</td><td>{r['old']}</td><td>{r['new']}</td>"
            f"<td>{delta_str}</td><td>{r['change']}</td></tr>"
        )

    html = f"""
    <html><head><meta charset='utf-8'><style>
    body {{ background-color:#0f1115; color:white; font-family:Segoe UI; }}
    table {{ width:100%; border-collapse:collapse; }}
    td,th {{ border:1px solid #333; padding:6px; }}
    tr:nth-child(even) {{ background:#151a22; }}
    </style></head>
    <body><h2>PatchForge Report</h2><table>
    <tr><th>Weapon</th><th>Metric</th><th>Old</th><th>New</th><th>Δ</th><th>Status</th></tr>
    {''.join(rows)}
    </table></body></html>
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ HTML exported: {path}")


# ---------------------------------------------------------
# CLI Commands
# ---------------------------------------------------------
def cmd_compare(args):
    """Compare two JSON files."""
    old_data = load_json(args.old)
    new_data = load_json(args.new)

    results = compare_jsons(old_data, new_data)
    summary = summarize_results(results)

    print("\n📊 PATCH COMPARISON SUMMARY")
    print("-" * 40)
    print(f"Buffs: {summary['buffs']}")
    print(f"Nerfs: {summary['nerfs']}")
    print(f"No Change: {summary['nochange']}")
    print(f"Mixed: {summary['mixed']}")
    print("-" * 40)

    # Output summary table to console
    for r in results[:10]:  # show only first 10 for brevity
        delta_str = "–" if r["delta"] is None else f"{r['delta']:+.2f}"
        print(f"{r['weapon']:<18} {r['metric']:<25} {delta_str:<6} {r['change']}")
    if len(results) > 10:
        print(f"... ({len(results)} total rows)")

    # Optional export
    if args.csv:
        export_csv(results, args.csv)
    if args.export:
        export_html(results, args.export)


def cmd_summary(args):
    """Display only aggregated summary data."""
    old_data = load_json(args.old)
    new_data = load_json(args.new)

    results = compare_jsons(old_data, new_data)
    summary = summarize_results(results)

    print("\n📈 PATCH SUMMARY")
    print("-" * 40)
    for k, v in summary.items():
        if k == "totals":
            continue
        print(f"{k.title():<10}: {v}")
    print("-" * 40)
    print("Net Δ by Metric:")
    for metric, delta in summary["totals"].items():
        print(f"  {metric:<25} {delta:+.2f}")


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="PatchForge CLI — Arc Raiders Patch Comparator"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # compare
    p_compare = sub.add_parser("compare", help="Compare two JSON files")
    p_compare.add_argument("old", help="Path to old JSON file")
    p_compare.add_argument("new", help="Path to new JSON file")
    p_compare.add_argument("--csv", help="Optional CSV export path")
    p_compare.add_argument("--export", help="Optional HTML export path")
    p_compare.set_defaults(func=cmd_compare)

    # summary
    p_summary = sub.add_parser("summary", help="Display summary only")
    p_summary.add_argument("old", help="Path to old JSON file")
    p_summary.add_argument("new", help="Path to new JSON file")
    p_summary.set_defaults(func=cmd_summary)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
