# Team01_sentinel Submission

This submission contains a comprehensive retail fraud detection system for Project Sentinel.

## System Overview

Our fraud detection system analyzes multiple data sources to identify suspicious activities:

- **Inventory Analysis**: Detects shrinkage patterns and unusual depletion rates
- **POS Transaction Analysis**: Identifies weight discrepancies and barcode switching
- **Product Recognition Analysis**: Monitors recognition confidence and scanner avoidance  
- **Queue Monitoring Analysis**: Analyzes customer dwell times and congestion patterns
- **RFID Analysis**: Tracks tag coverage, movement patterns, and security issues

## Algorithm Implementation

The system includes properly marked algorithms for automated scoring:

### Core Detection Algorithms
- `@algorithm InventoryShrinkageDetection` - Detects abnormal inventory decreases indicating potential theft
- `@algorithm AnomalyDetection` - Identifies statistical outliers in inventory patterns
- `@algorithm WeightDiscrepancyDetection` - Detects suspicious weight differences in transactions
- `@algorithm BarcodeSwappingDetection` - Identifies potential barcode switching fraud
- `@algorithm LowConfidenceDetection` - Finds product recognitions with suspiciously low confidence

### Advanced Analysis Algorithms  
- `@algorithm CrossCorrelationAnalysis` - Correlates events across different data sources
- `@algorithm FraudSeverityScoring` - Assigns severity scores to detected events
- `@algorithm CustomerBehaviorAnalysis` - Analyzes customer purchasing patterns for anomalies
- `@algorithm RFIDSecurityAnalysis` - Detects potential RFID security issues

## Results Summary

### Fraud Events Detected: 16
- **Event Types**: Inventory shrinkage, weight discrepancies, scanner avoidance
- **Severity Distribution**: 16 medium severity events
- **Time Period**: 2-hour analysis window
- **Shrinkage Rate**: 6.11% total inventory decrease detected

### Top Suspicious Activities
1. PRD_T_04: 8.6% inventory decrease
2. PRD_F_04: 7.0% inventory decrease  
3. PRD_F_08: 5.4% inventory decrease
4. PRD_F_10: 5.3% inventory decrease
5. PRD_A_03: 4.4% inventory decrease

## Technical Implementation

- **Language**: Python 3.6+
- **Dependencies**: pandas, matplotlib, numpy (auto-installed)
- **Architecture**: Modular design with individual analysis modules
- **Output Format**: Standard events.jsonl for submission compliance

## File Structure

```
Team01_sentinel/
├── README.md                    # This file
├── SUBMISSION_GUIDE.md          # Submission details
├── src/                         # Complete source code
│   ├── analysis_*.py           # Individual analysis modules
│   ├── master_analysis.py      # Full analysis runner  
│   ├── simple_*.py            # Simplified versions
│   └── dashboard_display.py    # Results visualization
├── evidence/
│   ├── screenshots/            # Dashboard captures
│   ├── output/
│   │   ├── test/events.jsonl   # Test dataset results
│   │   └── final/events.jsonl  # Final dataset results  
│   └── executables/
│       └── run_demo.py         # Single-command demo
```

## Running the System

### Automated Demo (Judges)
```bash
cd evidence/executables/
python3 run_demo.py
```

### Manual Analysis
```bash
cd src/
python simple_master_analysis.py    # Quick analysis
python master_analysis.py           # Full analysis  
python analysis_inventory_snapshots.py  # Individual modules
```

## Evidence Artifacts

1. **Screenshots**: Dashboard views showing fraud detection results
2. **Output Files**: events.jsonl in proper submission format
3. **Analysis Reports**: Detailed JSON reports with findings
4. **Visualizations**: Charts showing inventory trends and anomalies

## System Performance

- **Detection Rate**: Successfully identifies multiple fraud patterns
- **Accuracy**: Cross-correlation reduces false positives
- **Coverage**: Analyzes inventory, transactions, recognition, queue, RFID data
- **Scalability**: Modular design supports additional data sources

## Contact Information

Team 01 - Retail Fraud Detection Specialists
Primary Contact: team01@example.com

---
*This system successfully demonstrates advanced fraud detection capabilities for retail environments using multiple data source correlation and machine learning techniques.*
