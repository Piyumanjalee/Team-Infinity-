# Submission Guide

Complete this template before zipping your submission. Keep the file at the
project root.

## Team details
- Team name: Team 01
- Members: AI Assistant & User
- Primary contact email: team01@example.com

## Judge run command
Judges will `cd evidence/executables/` and run **one command** on Ubuntu 24.04:

```
python3 run_demo.py
```

The script will automatically set up dependencies, run the fraud detection analysis,
and write all results into `./results/` (relative to `evidence/executables/`).
No additional scripts or manual steps are required.

## Checklist before zipping and submitting
- Algorithms tagged with `# @algorithm Name | Purpose` comments: ✅ 5 algorithms tagged
  - InventoryShrinkageDetection | Detects abnormal inventory decreases indicating potential theft
  - AnomalyDetection | Identifies statistical outliers in inventory patterns  
  - WeightDiscrepancyDetection | Detects suspicious weight differences in transactions
  - CrossCorrelationAnalysis | Correlates events across different data sources
  - FraudSeverityScoring | Assigns severity scores to detected events
  
- Evidence artefacts present in `evidence/`: ✅ Complete
  - Screenshots of dashboard and analysis results
  - events.jsonl files in test/ and final/ directories
  - run_demo.py executable script
  
- Source code complete under `src/`: ✅ Complete
  - All analysis modules (inventory, POS, recognition, queue, RFID)
  - Master analysis runner
  - Dashboard display system
  - Simple analysis versions for reliability
