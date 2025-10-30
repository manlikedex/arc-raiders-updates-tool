import json
import os
import csv
import math
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from difflib import HtmlDiff

# Matplotlib for charts
import matplotlib
matplotlib.use("Agg")  # safer for some environments; switched to TkAgg on-demand
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------------------------------------------------
# SETTINGS HANDLER (auto-save last JSON paths)
# ---------------------------------------------------------
SETTINGS_FILE = "settings.json"

def load_settings() -> dict:
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_settings(data: dict):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


# ---------------------------------------------------------
# PATCHFORGE MAIN APP
# ---------------------------------------------------------
class PatchForgeApp:
    def __init__(self, root):
        self.root = root
        self.style = tb.Style("darkly")
        self.root.title("PatchForge PRO — Arc Raiders Patch Comparator")
        self.root.geometry("1260x820")

        self.settings = load_settings()
        self.old_path = self.settings.get("old_json", "")
        self.new_path = self.settings.get("new_json", "")
        self.old_data = {}
        self.new_data = {}

        # last comparison cache for summary
        self.last_rows = []          # list of (weapon, metric, old, new, delta, status_tag)
        self.metrics_cfg = [
            ("bodyDamage", True),
            ("headDamage", True),
            ("fireRate", True),
            ("magSize", True),
            ("timeToKill", False),
            ("bodyDamageAfterFirstHit", True),
            ("headDamageAfterFirstHit", True),
        ]

        self._build_ui()

    # -----------------------------------------------------
    # UI
    # -----------------------------------------------------
    def _build_ui(self):
        frm_top = tb.Frame(self.root, padding=10)
        frm_top.pack(fill=X)

        tb.Label(frm_top, text="PatchForge — Arc Raiders Patch Comparator", font=("Segoe UI", 14, "bold")).pack(side=LEFT, padx=10)

        tb.Button(frm_top, text="Load OLD JSON", bootstyle=SECONDARY, command=self.load_old_json).pack(side=LEFT, padx=5)
        self.lbl_old = tb.Label(frm_top, text=os.path.basename(self.old_path) if self.old_path else "(not loaded)", bootstyle=SECONDARY)
        self.lbl_old.pack(side=LEFT, padx=(0, 15))

        tb.Button(frm_top, text="Load NEW JSON", bootstyle=SECONDARY, command=self.load_new_json).pack(side=LEFT, padx=5)
        self.lbl_new = tb.Label(frm_top, text=os.path.basename(self.new_path) if self.new_path else "(not loaded)", bootstyle=SECONDARY)
        self.lbl_new.pack(side=LEFT, padx=(0, 15))

        tb.Button(frm_top, text="Compare", bootstyle=PRIMARY, command=self.compare).pack(side=LEFT, padx=10)
        tb.Button(frm_top, text="Summary", bootstyle=INFO, command=self.open_summary).pack(side=LEFT, padx=5)
        tb.Button(frm_top, text="Export CSV", bootstyle=SUCCESS, command=self.export_csv).pack(side=LEFT, padx=5)
        tb.Button(frm_top, text="Export HTML", bootstyle=INFO, command=self.export_html).pack(side=LEFT, padx=5)

        # table
        frm_table = tb.Frame(self.root)
        frm_table.pack(fill=BOTH, expand=YES, padx=10, pady=(5, 5))

        columns = ("Weapon", "Metric", "Old", "New", "Δ", "Status")
        self.tree = ttk.Treeview(frm_table, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            width = 180 if col == "Weapon" else 120
            self.tree.column(col, anchor=CENTER, width=width)
        self.tree.pack(side=LEFT, fill=BOTH, expand=YES)

        vsb = ttk.Scrollbar(frm_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side=RIGHT, fill=Y)

        self.tree.bind("<Double-1>", self.show_diff_popup)

        # Sticky legend bar
        legend = tb.Frame(self.root, padding=(10, 6), bootstyle="dark")
        legend.pack(fill=X, side=BOTTOM)

        def add_chip(frame, text, bootstyle):
            tb.Label(
                frame,
                text=text,
                bootstyle=bootstyle,
                padding=(8, 2),
                anchor=CENTER
            ).pack(side=LEFT, padx=(0, 6))

        tb.Label(legend, text="Legend:", bootstyle="secondary", padding=(4, 2)).pack(side=LEFT, padx=(0, 10))
        add_chip(legend, "🟩 Buff", "success")
        add_chip(legend, "🟥 Nerf", "danger")
        add_chip(legend, "🟨 Mixed", "warning")
        add_chip(legend, "⚪ No Change", "secondary")
        tb.Label(
            legend,
            text="   Severity: small = · | moderate = • | large = ●",
            bootstyle="secondary",
        ).pack(side=LEFT, padx=(12, 0))

    # -----------------------------------------------------
    # Loaders
    # -----------------------------------------------------
    def load_old_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.old_data = json.load(f)
            self.old_path = path
            self.lbl_old.config(text=os.path.basename(path))
            save_settings({"old_json": self.old_path, "new_json": self.new_path})
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file:\n{e}")

    def load_new_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.new_data = json.load(f)
            self.new_path = path
            self.lbl_new.config(text=os.path.basename(path))
            save_settings({"old_json": self.old_path, "new_json": self.new_path})
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file:\n{e}")

    # -----------------------------------------------------
    # Comparison logic
    # -----------------------------------------------------
    def compare(self):
        if not self.old_data or not self.new_data:
            messagebox.showwarning("Missing data", "Please load both OLD and NEW JSON files first.")
            return

        old_map = {w["name"]: w for w in self.old_data.get("weapons", [])}
        new_map = {w["name"]: w for w in self.new_data.get("weapons", [])}

        self.tree.delete(*self.tree.get_children())
        self.last_rows = []

        for name in sorted(set(old_map.keys()) | set(new_map.keys())):
            old = old_map.get(name, {}).get("stats", {})
            new = new_map.get(name, {}).get("stats", {})

            # classify the entire weapon after we compute all metrics
            statuses_for_weapon = []

            for key, higher_better in self.metrics_cfg:
                o = old.get(key)
                n = new.get(key)
                if (o is None) or (n is None):
                    change_txt = "⚪ Missing"
                    style = "secondary"
                    delta_str = "–"
                    delta_val = 0.0
                else:
                    delta_val = float(n) - float(o)
                    abs_delta = abs(delta_val)
                    if delta_val == 0:
                        change_txt = "⚪ No Change"
                        style = "secondary"
                    elif (higher_better and delta_val > 0) or ((not higher_better) and delta_val < 0):
                        style = "success"
                        dots = self.severity(abs_delta, key)
                        change_txt = f"🟩 Buff {dots}"
                        statuses_for_weapon.append("buff")
                    else:
                        style = "danger"
                        dots = self.severity(abs_delta, key)
                        change_txt = f"🟥 Nerf {dots}"
                        statuses_for_weapon.append("nerf")

                    delta_str = f"{delta_val:+.2f}"

                row = (name, key, o if o is not None else "", n if n is not None else "", delta_str, change_txt)
                self.tree.insert("", "end", values=row, tags=(style,))
                self.last_rows.append((name, key, o, n, delta_val, style))

            # If a weapon has both buffs and nerfs across metrics, tag a “mixed” summary line
            if "buff" in statuses_for_weapon and "nerf" in statuses_for_weapon:
                mix_row = (name, "— overall —", "", "", "", "🟨 Mixed")
                self.tree.insert("", "end", values=mix_row, tags=("warning",))
                self.last_rows.append((name, "— overall —", "", "", 0.0, "warning"))

        # Color rows
        self.tree.tag_configure("success", background="#18381a", foreground="#6fdc8c")
        self.tree.tag_configure("danger", background="#3a1818", foreground="#f28b82")
        self.tree.tag_configure("warning", background="#3a2e18", foreground="#fdd388")
        self.tree.tag_configure("secondary", background="#1e1e1e", foreground="#cccccc")

    # -----------------------------------------------------
    def severity(self, delta, key):
        thresholds = {
            "bodyDamage": (1, 5),
            "headDamage": (2, 8),
            "fireRate": (0.2, 1),
            "magSize": (1, 5),
            "timeToKill": (0.05, 0.2),
            "bodyDamageAfterFirstHit": (1, 5),
            "headDamageAfterFirstHit": (2, 8),
        }
        small, large = thresholds.get(key, (1, 5))
        if delta >= large:
            return "●"
        elif delta >= small:
            return "•"
        elif delta > 0:
            return "·"
        return ""

    # -----------------------------------------------------
    def show_diff_popup(self, event):
        item = self.tree.selection()
        if not item:
            return
        vals = self.tree.item(item[0], "values")
        metric = vals[1]
        o, n = vals[2], vals[3]

        win = tb.Toplevel(self.root)
        win.title(f"Diff — {vals[0]} ({metric})")
        win.geometry("700x450")

        diff_html = HtmlDiff().make_table(
            str(o).splitlines(), str(n).splitlines(),
            fromdesc="Old", todesc="New", context=True
        )
        text = tk.Text(win, wrap="word", bg="#121212", fg="#cccccc")
        text.insert("1.0", diff_html)
        text.config(state="disabled")
        text.pack(fill=BOTH, expand=YES)

    # -----------------------------------------------------
    def open_summary(self):
        if not self.last_rows:
            messagebox.showinfo("No Data", "Run a comparison first.")
            return

        # Aggregate
        counts = {"buff": 0, "nerf": 0, "mixed": 0, "nochange": 0}
        per_weapon_status = {}  # name -> set("buff"/"nerf")
        per_metric_delta = {}   # metric -> net delta

        for name, metric, o, n, delta, style in self.last_rows:
            # skip the added mixed summary rows when counting per-metric totals
            if metric == "— overall —":
                continue

            # classify cell
            if style == "success":
                counts["buff"] += 1
                per_weapon_status.setdefault(name, set()).add("buff")
            elif style == "danger":
                counts["nerf"] += 1
                per_weapon_status.setdefault(name, set()).add("nerf")
            elif style == "secondary":
                counts["nochange"] += 1

            # metric totals
            per_metric_delta[metric] = per_metric_delta.get(metric, 0.0) + (delta if isinstance(delta, (int, float)) else 0.0)

        # derive mixed from per-weapon sets
        mixed_weapons = sum(1 for s in per_weapon_status.values() if "buff" in s and "nerf" in s)
        counts["mixed"] = mixed_weapons

        # Top 5 buffs / nerfs by absolute delta across metrics
        # Build list of per-row magnitudes (ignoring missing/overall)
        cell_changes = [
            (name, metric, delta)
            for (name, metric, o, n, delta, style) in self.last_rows
            if metric != "— overall —" and isinstance(delta, (int, float))
        ]
        top_buffs = sorted([c for c in cell_changes if c[2] > 0.0], key=lambda x: -abs(x[2]))[:5]
        top_nerfs = sorted([c for c in cell_changes if c[2] < 0.0], key=lambda x: -abs(x[2]))[:5]

        # ----- UI window
        win = tb.Toplevel(self.root)
        win.title("Patch Summary Report")
        win.geometry("980x720")
        win.grab_set()

        # Layout: top info, charts row, lists
        info = tb.Frame(win, padding=10)
        info.pack(fill=X)
        tb.Label(info, text="Patch Summary", font=("Segoe UI", 16, "bold")).pack(side=LEFT)
        tb.Label(info, text=f"  Buff cells: {counts['buff']}   Nerf cells: {counts['nerf']}   No-change cells: {counts['nochange']}   Mixed weapons: {counts['mixed']}",
                 bootstyle="secondary").pack(side=LEFT, padx=12)

        charts = tb.Frame(win, padding=(10, 0))
        charts.pack(fill=BOTH, expand=YES)

        left = tb.Labelframe(charts, text="Changes Distribution", padding=10)
        right = tb.Labelframe(charts, text="Net Δ by Metric", padding=10)
        left.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 5), pady=5)
        right.pack(side=LEFT, fill=BOTH, expand=YES, padx=(5, 0), pady=5)

        # PIE CHART
        fig1 = Figure(figsize=(4.6, 3.4), dpi=100)
        ax1 = fig1.add_subplot(111)
        labels = ["Buff", "Nerf", "Mixed", "No change"]
        sizes = [counts["buff"], counts["nerf"], counts["mixed"], counts["nochange"]]
        # avoid all zeros crash
        if sum(sizes) == 0:
            sizes = [1, 0, 0, 0]
        ax1.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90
        )
        ax1.axis("equal")
        FigureCanvasTkAgg(fig1, master=left).get_tk_widget().pack(fill=BOTH, expand=YES)

        # BAR CHART
        fig2 = Figure(figsize=(4.6, 3.4), dpi=100)
        ax2 = fig2.add_subplot(111)
        metrics = list(per_metric_delta.keys())
        values = [per_metric_delta[m] for m in metrics]
        if not metrics:
            metrics = ["(none)"]
            values = [0]
        ax2.bar(metrics, values)
        ax2.set_ylabel("Net Δ (sum of new - old)")
        ax2.set_xticklabels(metrics, rotation=20, ha="right")
        FigureCanvasTkAgg(fig2, master=right).get_tk_widget().pack(fill=BOTH, expand=YES)

        # Lists for top changes
        lists = tb.Frame(win, padding=10)
        lists.pack(fill=BOTH, expand=YES)

        lf_buffs = tb.Labelframe(lists, text="Top 5 Buffs (by absolute Δ)", padding=10)
        lf_nerfs = tb.Labelframe(lists, text="Top 5 Nerfs (by absolute Δ)", padding=10)
        lf_buffs.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 5))
        lf_nerfs.pack(side=LEFT, fill=BOTH, expand=YES, padx=(5, 0))

        def listbox_from(items, parent):
            lb = tk.Listbox(parent, bg="#0f1115", fg="#d0d0d0", highlightthickness=0, relief="flat")
            for (w, m, d) in items:
                lb.insert(END, f"{w} — {m}: {d:+.2f}")
            lb.pack(fill=BOTH, expand=YES)

        listbox_from(top_buffs, lf_buffs)
        listbox_from(top_nerfs, lf_nerfs)

    # -----------------------------------------------------
    def export_csv(self):
        if not self.tree.get_children():
            messagebox.showinfo("No Data", "Run a comparison first.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Weapon", "Metric", "Old", "New", "Δ", "Status"])
            for child in self.tree.get_children():
                writer.writerow(self.tree.item(child, "values"))

        messagebox.showinfo("Saved", f"CSV exported:\n{path}")

    def export_html(self):
        if not self.tree.get_children():
            messagebox.showinfo("No Data", "Run a comparison first.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML", "*.html")])
        if not path:
            return

        rows = []
        for child in self.tree.get_children():
            vals = self.tree.item(child, "values")
            rows.append(f"<tr><td>{'</td><td>'.join(map(lambda x: '' if x is None else str(x), vals))}</td></tr>")

        html = f"""
        <html>
        <head><meta charset="utf-8"><style>
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

        messagebox.showinfo("Saved", f"HTML exported:\n{path}")


# ---------------------------------------------------------
# Run
# ---------------------------------------------------------
if __name__ == "__main__":
    # switch backend now that Tk exists
    import matplotlib
    matplotlib.use("TkAgg")

    app = tb.Window(themename="darkly")
    PatchForgeApp(app)
    app.mainloop()
