PatchForge — the Arc Raiders patch data comparison & analytics tool.

🧾 README.md
# ⚙️ PatchForge 
### Arc Raiders Patch Comparator & Data Intelligence Toolkit  


PatchForge is an advanced data analysis and patch comparison tool built for the **Arc Raiders** community and developers.  
It helps you instantly detect, visualize, and summarize balance changes between game patches — highlighting buffs, nerfs, and mixed adjustments across all weapons and stats.

---

## 🎯 Features

✅ **Smart JSON Comparison**  
Compare old and new Arc Raiders weapon datasets side-by-side with stat deltas and automatic buff/nerf detection.  

✅ **Color-Coded Visual UI**  
Modern dark UI built with [`ttkbootstrap`](https://github.com/israel-dryer/ttkbootstrap), showing green (buffs), red (nerfs), yellow (mixed), and gray (no changes).  

✅ **Interactive Charts & Summaries**  
Pie and bar charts show the overall patch balance state and per-stat net deltas.  

✅ **Automatic Patch Summary Export**  
Generate beautiful, ready-to-share HTML or CSV summaries of all stat changes.  

✅ **Weapon Image Integration** *(coming soon)*  
Displays weapon thumbnails in both the GUI and export reports.  

✅ **Discord Webhook Alerts** *(in development)*  
Automatically post patch summaries and top balance changes directly to your Discord server.  

✅ **CLI + GUI Support**  
Use the tool interactively or via automation:
```bash
python patchforge_cli.py compare old.json new.json --export summary.html

🧠 How It Works

PatchForge PRO+ compares game data between two JSON snapshots (e.g., pre-patch and post-patch) from the Arc Raiders API or your local files.

Each weapon’s core stats are analyzed:

bodyDamage

headDamage

fireRate

magSize

timeToKill

bodyDamageAfterFirstHit

headDamageAfterFirstHit

Then it:

Calculates deltas

Detects buffs, nerfs, or neutral changes

Visualizes results in a modern GUI

Exports summaries (CSV, HTML, or chart dashboard)

🖥️ Desktop App (GUI)

Run the modern visual interface:

python patchforge_pro_colored_summary.py


Features:

Load old.json and new.json

Compare instantly

View results in an interactive table

Double-click any row to view differences

Export to CSV or HTML

Generate patch overview charts

⚙️ Command-Line Mode (CLI)

Use PatchForge directly in your console:

# Compare and print summary
python patchforge_cli.py compare data/old.json data/new.json

# Export report to HTML
python patchforge_cli.py compare data/old.json data/new.json --export patch_summary.html

# Export to CSV
python patchforge_cli.py compare data/old.json data/new.json --csv patch_diff.csv

# Display aggregated summary
python patchforge_cli.py summary data/old.json data/new.json

🧩 Folder Structure
PatchForge/
│
├── patchforge_core.py               # Core comparison engine
├── patchforge.py # GUI application
├── patchforge_cli.py                # CLI version
├── settings.json                    # Saved JSON paths
└── data/
    ├── old.json
    └── new.json

🧰 Build as Executable (Windows)

Install dependencies:

pip install pyinstaller ttkbootstrap matplotlib


Build GUI version:

python -m PyInstaller --noconfirm --noconsole --onefile --windowed patchforge_pro_colored_summary.py


Build CLI version:

python -m PyInstaller --noconfirm --onefile patchforge_cli.py


The .exe files will appear inside the dist/ folder.

🧱 Tech Stack
Component	Description
Python 3.11+	Core language
ttkbootstrap	Modern dark UI
matplotlib	Summary chart visualization
PyInstaller	EXE build support
JSON/CSV/HTML	Export formats
Discord Webhooks (coming soon)	Patch alerts
🧪 Roadmap
Phase	Feature	Status
1	Modular Core & CLI	✅ Done
2	Auto Patch Detection (MetaForge API)	🚧 In Progress
3	Discord Webhook Alerts	🧠 Planned
4	Weapon Images in GUI & Reports	🧱 Planned
5	PatchForge Monitor (auto background checker)	🔮 Planned
6	Flask Web Dashboard	🕸️ Future Phase
💬 Example Output
📊 PATCH COMPARISON SUMMARY

----------------------------------------
Buffs: 5
Nerfs: 3
No Change: 2
Mixed: 1
----------------------------------------

Anvil III         bodyDamage             +4.00  Buff ●
Ferro II          fireRate               -1.00  Nerf •
Kettle I          magSize                +1.00  Buff ·
...
✅ HTML exported: patch_summary.html

👥 Contributing

Contributions are welcome — if you want to improve patch detection, UI design, or web export features:

Fork this repo

Commit your changes

Open a pull request

📜 License

MIT License © 2025 Dex
Open-source and free for the Arc Raiders community.
