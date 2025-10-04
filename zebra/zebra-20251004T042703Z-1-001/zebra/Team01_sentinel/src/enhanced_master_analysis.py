#!/usr/bin/env python3
"""
Enhanced Master Analysis - Works with Default and Uploaded Data
============================================================
Automatically detects and uses uploaded data files if available
"""

import json
import os
from datetime import datetime

def get_data_source_path(filename):
    """Get the path to data file, preferring uploads over default"""
    upload_path = f"data/uploads/{filename}"
    default_path = f"data/input/{filename}"
    
    if os.path.exists(upload_path):
        print(f"   📤 Using uploaded: {filename}")
        return upload_path
    elif os.path.exists(default_path):
        print(f"   📁 Using default: {filename}")
        return default_path
    else:
        print(f"   ❌ Missing: {filename}")
        return None

def load_inventory_data():
    """Load inventory data from available source"""
    file_path = get_data_source_path("inventory_snapshots.jsonl")
    if not file_path:
        return []
    
    data = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return data
    except Exception as e:
        print(f"   Error loading inventory data: {e}")
        return []

def load_pos_data():
    """Load POS transaction data from available source"""
    file_path = get_data_source_path("pos_transactions.jsonl")
    if not file_path:
        return []
    
    data = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return data
    except Exception as e:
        print(f"   Error loading POS data: {e}")
        return []

def load_product_recognition_data():
    """Load product recognition data from available source"""
    file_path = get_data_source_path("product_recognition.jsonl")
    if not file_path:
        return []
    
    data = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return data
    except Exception as e:
        print(f"   Error loading product recognition data: {e}")
        return []

def load_queue_data():
    """Load queue monitoring data from available source"""
    file_path = get_data_source_path("queue_monitoring.jsonl")
    if not file_path:
        return []
    
    data = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return data
    except Exception as e:
        print(f"   Error loading queue data: {e}")
        return []

def load_rfid_data():
    """Load RFID readings data from available source"""
    file_path = get_data_source_path("rfid_readings.jsonl")
    if not file_path:
        return []
    
    data = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return data
    except Exception as e:
        print(f"   Error loading RFID data: {e}")
        return []

def analyze_inventory_shrinkage(inventory_data):
    """Analyze inventory for shrinkage events"""
    if not inventory_data:
        return []
    
    shrinkage_events = []
    
    # Sort data by timestamp
    sorted_data = sorted(inventory_data, key=lambda x: x.get('timestamp', ''))
    
    # Compare consecutive snapshots
    for i in range(1, len(sorted_data)):
        prev_snapshot = sorted_data[i-1].get('data', {})
        curr_snapshot = sorted_data[i].get('data', {})
        timestamp = sorted_data[i].get('timestamp')
        
        # Check each product for decreases
        for product in prev_snapshot:
            if product in curr_snapshot:
                prev_qty = prev_snapshot[product]
                curr_qty = curr_snapshot[product]
                
                if curr_qty < prev_qty:
                    decrease_pct = ((prev_qty - curr_qty) / prev_qty) * 100
                    
                    # Only flag significant decreases (>3%)
                    if decrease_pct >= 3.0:
                        severity = "HIGH" if decrease_pct >= 10 else "MEDIUM"
                        
                        shrinkage_events.append({
                            "timestamp": timestamp,
                            "product": product,
                            "previous_qty": prev_qty,
                            "current_qty": curr_qty,
                            "decrease_percentage": decrease_pct,
                            "severity": severity
                        })
    
    return shrinkage_events

def analyze_pos_transactions(pos_data):
    """Analyze POS transactions for anomalies"""
    if not pos_data:
        return []
    
    weight_discrepancies = []
    
    # Expected weights for common product categories
    expected_weights = {
        "PRD_F": 400,  # Food items ~400g
        "PRD_B": 500,  # Beverages ~500g
        "PRD_A": 100,  # Accessories ~100g
        "PRD_S": 200,  # Snacks ~200g
        "PRD_V": 300,  # Vegetables ~300g
        "PRD_H": 150,  # Health items ~150g
        "PRD_C": 250,  # Cosmetics ~250g
        "PRD_T": 300   # Textiles ~300g
    }
    
    for transaction in pos_data:
        try:
            data = transaction.get('data', {})
            sku = data.get('sku', '')
            actual_weight = data.get('weight_g', 0)
            
            # Get expected weight based on product category
            category = sku.split('_')[0] + '_' + sku.split('_')[1]
            expected_weight = expected_weights.get(category, 300)
            
            # Check for significant weight discrepancy (>15%)
            if actual_weight > 0:
                weight_diff_pct = abs(actual_weight - expected_weight) / expected_weight * 100
                
                if weight_diff_pct > 15:
                    weight_discrepancies.append({
                        "timestamp": transaction.get('timestamp'),
                        "sku": sku,
                        "expected_weight": expected_weight,
                        "actual_weight": actual_weight,
                        "discrepancy_percentage": weight_diff_pct,
                        "severity": "MEDIUM"
                    })
        except Exception:
            continue
    
    return weight_discrepancies

def analyze_product_recognition(recognition_data):
    """Analyze product recognition confidence"""
    if not recognition_data:
        return []
    
    low_confidence_events = []
    
    for event in recognition_data:
        try:
            data = event.get('data', {})
            accuracy = data.get('accuracy', 1.0)
            
            # Flag low confidence recognition (<70%)
            if accuracy < 0.7:
                low_confidence_events.append({
                    "timestamp": event.get('timestamp'),
                    "predicted_product": data.get('predicted_product'),
                    "confidence": accuracy,
                    "severity": "LOW" if accuracy > 0.5 else "MEDIUM"
                })
        except Exception:
            continue
    
    return low_confidence_events

def analyze_queue_behavior(queue_data):
    """Analyze queue monitoring for suspicious behavior"""
    if not queue_data:
        return []
    
    dwell_anomalies = []
    
    for event in queue_data:
        try:
            data = event.get('data', {})
            avg_dwell_time = data.get('average_dwell_time', 0)
            customer_count = data.get('customer_count', 0)
            
            # Flag unusually long dwell times (>5 minutes)
            if avg_dwell_time > 300 and customer_count > 0:
                dwell_anomalies.append({
                    "timestamp": event.get('timestamp'),
                    "station_id": event.get('station_id'),
                    "dwell_time": avg_dwell_time,
                    "customer_count": customer_count,
                    "severity": "MEDIUM"
                })
        except Exception:
            continue
    
    return dwell_anomalies

def analyze_rfid_coverage(rfid_data):
    """Analyze RFID coverage and security"""
    if not rfid_data:
        return {"detection_rate": 0, "security_events": []}
    
    total_readings = len(rfid_data)
    valid_readings = 0
    security_events = []
    
    for event in rfid_data:
        try:
            data = event.get('data', {})
            epc = data.get('epc')
            location = data.get('location')
            sku = data.get('sku')
            
            if epc and location and sku:
                valid_readings += 1
        except Exception:
            continue
    
    detection_rate = (valid_readings / total_readings * 100) if total_readings > 0 else 0
    
    return {
        "detection_rate": detection_rate,
        "security_events": security_events,
        "total_readings": total_readings,
        "valid_readings": valid_readings
    }

def main():
    """Main enhanced analysis function"""
    print("============================================================")
    print("PROJECT SENTINEL - ENHANCED FRAUD DETECTION")
    print("============================================================")
    print("🔍 Checking data sources...")
    
    # Check which data sources are available
    data_sources = {
        "inventory_snapshots.jsonl": False,
        "pos_transactions.jsonl": False,
        "product_recognition.jsonl": False,
        "queue_monitoring.jsonl": False,
        "rfid_readings.jsonl": False
    }
    
    for filename in data_sources:
        upload_path = f"data/uploads/{filename}"
        default_path = f"data/input/{filename}"
        if os.path.exists(upload_path) or os.path.exists(default_path):
            data_sources[filename] = True
    
    all_events = []
    analysis_results = {}
    
    # 1. Inventory Analysis
    print("\n1. Analyzing Inventory Data...")
    inventory_data = load_inventory_data()
    shrinkage_events = analyze_inventory_shrinkage(inventory_data)
    all_events.extend([{**event, "event_type": "INVENTORY_SHRINKAGE"} for event in shrinkage_events])
    analysis_results['inventory'] = {
        "shrinkage_events": shrinkage_events,
        "total_events": len(shrinkage_events)
    }
    print(f"   ✓ Found {len(shrinkage_events)} shrinkage events")
    
    # 2. POS Analysis
    print("\n2. Analyzing POS Transaction Data...")
    pos_data = load_pos_data()
    weight_discrepancies = analyze_pos_transactions(pos_data)
    all_events.extend([{**event, "event_type": "WEIGHT_DISCREPANCY"} for event in weight_discrepancies])
    analysis_results['pos'] = {
        "weight_discrepancies": weight_discrepancies,
        "total_events": len(weight_discrepancies)
    }
    print(f"   ✓ Found {len(weight_discrepancies)} weight discrepancies")
    
    # 3. Product Recognition Analysis
    print("\n3. Analyzing Product Recognition Data...")
    recognition_data = load_product_recognition_data()
    low_confidence_events = analyze_product_recognition(recognition_data)
    all_events.extend([{**event, "event_type": "LOW_CONFIDENCE"} for event in low_confidence_events])
    analysis_results['recognition'] = {
        "low_confidence_events": low_confidence_events,
        "total_events": len(low_confidence_events)
    }
    print(f"   ✓ Found {len(low_confidence_events)} low confidence events")
    
    # 4. Queue Analysis
    print("\n4. Analyzing Queue Data...")
    queue_data = load_queue_data()
    dwell_anomalies = analyze_queue_behavior(queue_data)
    all_events.extend([{**event, "event_type": "DWELL_ANOMALY"} for event in dwell_anomalies])
    analysis_results['queue'] = {
        "dwell_anomalies": dwell_anomalies,
        "total_events": len(dwell_anomalies)
    }
    print(f"   ✓ Found {len(dwell_anomalies)} dwell time anomalies")
    
    # 5. RFID Analysis
    print("\n5. Analyzing RFID Data...")
    rfid_data = load_rfid_data()
    rfid_results = analyze_rfid_coverage(rfid_data)
    analysis_results['rfid'] = rfid_results
    print(f"   ✓ RFID detection rate: {rfid_results['detection_rate']:.1f}%")
    
    # Generate comprehensive report
    print("\n============================================================")
    print("ENHANCED FRAUD DETECTION ANALYSIS COMPLETE")
    print("============================================================")
    
    total_events = len(all_events)
    high_severity = len([e for e in all_events if e.get('severity') == 'HIGH'])
    medium_severity = len([e for e in all_events if e.get('severity') == 'MEDIUM'])
    
    print(f"Total Events Detected: {total_events}")
    print(f"High Severity Events: {high_severity}")
    print(f"Medium Severity Events: {medium_severity}")
    
    # Count event types
    event_types = {}
    for event in all_events:
        event_type = event.get('event_type', 'UNKNOWN')
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    print(f"\nEvent Types:")
    for event_type, count in event_types.items():
        print(f"  - {event_type}: {count}")
    
    # Generate output files
    os.makedirs("output", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # Save events for submission
    with open("output/events.jsonl", "w") as f:
        for event in all_events:
            f.write(json.dumps(event) + "\n")
    
    # Generate inventory report (for dashboard compatibility)
    if shrinkage_events:
        inventory_summary = {
            "initial_inventory": 0,
            "final_inventory": 0,
            "net_change": 0
        }
        
        # Calculate inventory summary from first and last snapshots
        if inventory_data and len(inventory_data) >= 2:
            first_snapshot = inventory_data[0].get('data', {})
            last_snapshot = inventory_data[-1].get('data', {})
            
            initial_total = sum(first_snapshot.values())
            final_total = sum(last_snapshot.values())
            
            inventory_summary = {
                "initial_inventory": initial_total,
                "final_inventory": final_total,
                "net_change": final_total - initial_total
            }
        
        inventory_report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "data_source": "Enhanced Analysis (Multiple Sources)",
            "shrinkage_events": shrinkage_events,
            "summary": inventory_summary
        }
        
        with open("inventory_analysis_report.json", "w") as f:
            json.dump(inventory_report, f, indent=2)
    
    # Save comprehensive report
    comprehensive_report = {
        "analysis_timestamp": datetime.now().isoformat(),
        "data_sources_used": data_sources,
        "results": analysis_results,
        "summary": {
            "total_events": total_events,
            "high_severity_events": high_severity,
            "medium_severity_events": medium_severity,
            "event_types": event_types
        }
    }
    
    with open("reports/enhanced_analysis_report.json", "w") as f:
        json.dump(comprehensive_report, f, indent=2)
    
    print(f"\nFiles Generated:")
    print(f"  - output/events.jsonl (for submission)")
    print(f"  - inventory_analysis_report.json (for dashboard)")
    print(f"  - reports/enhanced_analysis_report.json (comprehensive report)")
    
    return 0

if __name__ == "__main__":
    main()
