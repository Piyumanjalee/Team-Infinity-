#!/usr/bin/env python3
"""
Project Sentinel Setup Script
=============================

This script helps set up your Project Sentinel analysis environment.
It checks dependencies, creates necessary directories, and provides
instructions for running the analysis.

Usage: python setup.py
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is adequate"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("❌ Python 3.6 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True

def create_directories():
    """Create necessary directories for analysis"""
    print("\nCreating directory structure...")
    
    directories = [
        "output",
        "reports", 
        "plots",
        "evidence/output/test",
        "evidence/output/final",
        "evidence/executables"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created/verified: {directory}/")

def check_data_files():
    """Check if required data files are present"""
    print("\nChecking data files...")
    
    required_files = [
        "data/input/inventory_snapshots.jsonl",
        "data/input/pos_transactions.jsonl", 
        "data/input/product_recognition.jsonl",
        "data/input/queue_monitoring.jsonl",
        "data/input/rfid_readings.jsonl"
    ]
    
    all_present = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_present = False
    
    return all_present

def check_analysis_modules():
    """Check if analysis modules are present"""
    print("\nChecking analysis modules...")
    
    required_modules = [
        "analysis_inventory_snapshots.py",
        "analysis_pos_transactions.py",
        "analysis_product_recognition.py", 
        "analysis_queue_monitoring.py",
        "analysis_rfid_readings.py",
        "master_analysis.py"
    ]
    
    all_present = True
    for module in required_modules:
        if os.path.exists(module):
            print(f"✅ Found: {module}")
        else:
            print(f"❌ Missing: {module}")
            all_present = False
    
    return all_present

def create_run_demo_script():
    """Create the run_demo.py script for evidence/executables/"""
    print("\nCreating run_demo.py script...")
    
    demo_script_content = '''#!/usr/bin/env python3
"""
Project Sentinel Demo Runner
============================

This script demonstrates the Project Sentinel fraud detection system.
Run this script to execute the full analysis pipeline.

Usage: python run_demo.py
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path to import analysis modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Main demo execution"""
    print("="*60)
    print("PROJECT SENTINEL FRAUD DETECTION DEMO")
    print("="*60)
    print(f"Analysis started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Change to project root directory
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    try:
        # Import and run master analysis
        from master_analysis import main as run_analysis
        
        print("\\nStarting fraud detection analysis...")
        run_analysis()
        
        print("\\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("="*60)
        print("Check the following files for results:")
        print("- output/events.jsonl - Final events for submission")
        print("- reports/master_analysis_report.json - Detailed analysis")
        print("- Individual module reports in current directory")
        
    except Exception as e:
        print(f"\\n❌ Demo failed with error: {str(e)}")
        return 1
    finally:
        os.chdir(original_dir)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
    
    os.makedirs("evidence/executables", exist_ok=True)
    with open("evidence/executables/run_demo.py", "w") as f:
        f.write(demo_script_content)
    
    print("✅ Created: evidence/executables/run_demo.py")

def create_readme():
    """Create a README with instructions"""
    print("\nCreating README file...")
    
    readme_content = '''# Project Sentinel Fraud Detection System

## Overview
This is a comprehensive retail fraud detection system that analyzes multiple data sources to identify suspicious activities including theft, barcode switching, scanner avoidance, and other fraudulent behaviors.

## Analysis Modules

### 1. Inventory Analysis (`analysis_inventory_snapshots.py`)
- Detects inventory shrinkage patterns
- Identifies unusual product depletion rates
- Flags potential theft or misplacement events

### 2. POS Transaction Analysis (`analysis_pos_transactions.py`)
- Detects weight discrepancies between expected and actual weights
- Identifies suspected barcode switching attempts
- Analyzes customer behavior patterns

### 3. Product Recognition Analysis (`analysis_product_recognition.py`)
- Monitors product recognition confidence scores
- Detects potential scanner avoidance patterns
- Identifies problematic products with low recognition rates

### 4. Queue Monitoring Analysis (`analysis_queue_monitoring.py`)
- Analyzes customer dwell times for anomalies
- Detects congestion patterns and bottlenecks
- Identifies operational efficiency issues

### 5. RFID Analysis (`analysis_rfid_readings.py`)
- Monitors RFID tag coverage and performance
- Tracks tag movement patterns
- Detects potential security issues like tag cloning

## Quick Start

1. **Run Individual Analysis:**
   ```bash
   python analysis_inventory_snapshots.py
   python analysis_pos_transactions.py
   python analysis_product_recognition.py
   python analysis_queue_monitoring.py
   python analysis_rfid_readings.py
   ```

2. **Run Complete Analysis:**
   ```bash
   python master_analysis.py
   ```

3. **Run Demo (for submission):**
   ```bash
   python evidence/executables/run_demo.py
   ```

## Output Files

- `output/events.jsonl` - Final events in submission format
- `reports/master_analysis_report.json` - Comprehensive analysis report
- Individual module reports: `*_analysis_report.json`
- Visualization data in `plots/` directory

## Algorithm Markers

The system includes properly marked algorithms for automated scoring:
- `@algorithm InventoryShrinkageDetection` - Detects abnormal inventory decreases
- `@algorithm WeightDiscrepancyDetection` - Identifies suspicious weight differences
- `@algorithm LowConfidenceDetection` - Finds low-confidence product recognitions
- `@algorithm DwellTimeAnomalyDetection` - Detects unusual customer dwell times
- `@algorithm RFIDCoverageAnalysis` - Analyzes RFID tag coverage
- `@algorithm CrossCorrelationAnalysis` - Correlates events across data sources

## Event Types Detected

1. **INVENTORY_SHRINKAGE** - Unexplained inventory decreases
2. **WEIGHT_DISCREPANCY** - Mismatched product weights
3. **BARCODE_SWITCHING** - Suspected barcode manipulation
4. **SCANNER_AVOIDANCE** - Products not properly scanned
5. **CHECKOUT_DIFFICULTY** - Unusual customer dwell times
6. **CORRELATED_FRAUD_ATTEMPT** - Multiple indicators suggesting fraud

## Dependencies

- Python 3.6+
- Standard library modules only (no external dependencies required)
- Optional: pandas, matplotlib for enhanced visualization (analysis works without them)

## File Structure

```
project-sentinel/
├── data/input/                    # Input data files
├── output/                        # Generated events.jsonl
├── reports/                       # Detailed analysis reports
├── plots/                         # Visualization outputs
├── evidence/executables/          # Demo scripts
├── analysis_*.py                  # Individual analysis modules
├── master_analysis.py             # Complete analysis runner
└── README.md                      # This file
```

## Troubleshooting

1. **Missing modules error**: Ensure all analysis_*.py files are in the same directory
2. **File not found**: Check that data/input/ contains all required JSONL files
3. **Permission errors**: Ensure write permissions for output directories

## Contact

For questions about this fraud detection system, refer to the Project Sentinel documentation.
'''
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("✅ Created: README.md")

def main():
    """Main setup function"""
    print("Project Sentinel Setup")
    print("="*30)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create directories
    create_directories()
    
    # Check data files
    data_present = check_data_files()
    
    # Check analysis modules
    modules_present = check_analysis_modules()
    
    # Create demo script
    create_run_demo_script()
    
    # Create README
    create_readme()
    
    # Final status
    print("\n" + "="*50)
    print("SETUP COMPLETE")
    print("="*50)
    
    if data_present and modules_present:
        print("✅ All required files are present!")
        print("\nNext steps:")
        print("1. Run individual analysis: python analysis_inventory_snapshots.py")
        print("2. Run complete analysis: python master_analysis.py")
        print("3. Run demo: python evidence/executables/run_demo.py")
    else:
        print("⚠️  Some required files are missing.")
        if not data_present:
            print("   - Ensure all JSONL data files are in data/input/")
        if not modules_present:
            print("   - Ensure all analysis Python modules are present")
    
    print("\nSetup files created:")
    print("- Directory structure")
    print("- evidence/executables/run_demo.py")
    print("- README.md")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
