# Team-Infinity-
Project Sentinel — Team Infinity

Overview
--------
This repository contains Team Infinity submission for Project Sentinel: a modular retail fraud detection system. The project ingests inventory snapshots, POS transactions, product recognition outputs, queue monitoring data, and RFID readings to detect suspicious activity, score events, and produce submission-formatted outputs and visual evidence.

Team Details
-Team name :- Infinity

Quick start
-----------
Prerequisites
- Python 3.9+ (3.11 recommended)
- Git (optional)

Install (recommended: use a virtual environment)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install --user pandas numpy matplotlib streamlit
```

Run demo (produces `events.jsonl` and sample reports)

```powershell
cd zebra/zebra-20251004T042703Z-1-001/zebra/Team01_sentinel/evidence/executables
python run_demo.py
```

View dashboard (optional)

```powershell
cd zebra/zebra-20251004T042703Z-1-001/zebra
python -m streamlit run dashboard_display.py --server.enableCORS false --server.enableXsrfProtection false
# open http://localhost:8501 in your browser
```

Repository layout
-----------------
- zebra/...
  - Team01_sentinel/
    - README.md                # Submission-specific README (kept inside folder)
    - SUBMISSION_GUIDE.md     # Submission checklist
    - src/                    # Analysis modules and master scripts
    - evidence/               # Demo runner, screenshots, and generated outputs

Submission outputs
------------------
- evidence/output/events.jsonl  — submission-formatted events
- src/inventory_analysis_report.json — detailed analysis report
- evidence/output/plots/*.png   — visual evidence

Notes
-----
- The demo (`run_demo.py`) is the quickest way to generate submission outputs used for evidence and screenshots.
- If you encounter Unicode/emoji printing issues on Windows consoles, run Python with UTF-8 mode (set environment variable `PYTHONUTF8=1` or run with `-X utf8`).

