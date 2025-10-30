# PatchForge — Arc Raiders Patch Comparator (GUI)

A standalone GUI tool that compares two Arc Raiders data snapshots (JSON) and detects:
- 🟢 New weapons
- 🔴 Removed weapons
- 🟡 Updated weapons
- 🟩 Buffs and 🟥 Nerfs on key stats

**Tracked stats:** `bodyDamage`, `headDamage`, `fireRate`, `magSize`, `timeToKill`, `bodyDamageAfterFirstHit`, `headDamageAfterFirstHit`  
*(Note: lower `timeToKill` is considered a Buff; others treat higher as better.)*

## ▶️ Quick Start

```bash
pip install -r requirements.txt
python patchforge.py
```

By default, the app points to the sample files in `data/old.json` and `data/new.json`. Click **Compare** to view differences and **Export Markdown** to generate a report under `reports/`.

## 🗂️ Project Structure

```
PatchForge/
 ├── patchforge.py           # GUI app
 ├── data/
 │    ├── old.json           # sample old dataset
 │    └── new.json           # sample new dataset (with changes)
 ├── reports/                # exported reports (created after export)
 ├── utils/                  # reserved for future helpers
 └── requirements.txt
```

## 💡 Notes
- The GUI uses a dark modern theme via **ttkbootstrap**.
- `timeToKill` is the only stat where *lower is better*.
- No internet connection is required; this package ships with sample data.
