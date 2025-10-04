#!/usr/bin/env python3
"""
Manual Data Analysis Module
=========================
Analyzes manually entered data for fraud detection
"""

import json
import os
from datetime import datetime

def load_manual_data(filename):
    """Load manually entered data"""
    file_path = f"data/manual/{filename}"
    if not os.path.exists(file_path):
        return []
    
    data = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        print(f"   ✓ Loaded {len(data)} records from {filename}")
        return data
    except Exception as e:
        print(f"   ❌ Error loading {filename}: {e}")
        return []

def analyze_manual_inventory(inventory_data):
    """Analyze manually entered inventory data for shrinkage"""
    if not inventory_data:
        return []
    
    shrinkage_events = []
    
    # Sort data by timestamp
    sorted_data = sorted(inventory_data, key=lambda x: x.get('timestamp', ''))
    
    if len(sorted_data) < 2:
        return shrinkage_events
    
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
                    
                    # Flag significant decreases (>2% for manual data sensitivity)
                    if decrease_pct >= 2.0:
                        severity = "HIGH" if decrease_pct >= 8 else "MEDIUM"
                        
                        shrinkage_events.append({
                            "timestamp": timestamp,
                            "product": product,
                            "previous_qty": prev_qty,
                            "current_qty": curr_qty,
                            "decrease_percentage": decrease_pct,
                            "severity": severity
                        })
    
    return shrinkage_events

def analyze_manual_pos(pos_data):
    """Analyze manually entered POS data"""
    if not pos_data:
        return []
    
    anomalies = []
    
    # Expected price ranges for product categories
    expected_prices = {
        "PRD_F": (200, 800),   # Food items
        "PRD_B": (150, 600),   # Beverages  
        "PRD_A": (50, 500),    # Accessories
        "PRD_S": (100, 400),   # Snacks
        "PRD_V": (50, 300),    # Vegetables
        "PRD_H": (200, 1000),  # Health items
        "PRD_C": (300, 1200),  # Cosmetics
        "PRD_T": (500, 2000)   # Textiles
    }
    
    for transaction in pos_data:
        try:
            data = transaction.get('data', {})
            sku = data.get('sku', '')
            price = data.get('price', 0)
            
            if sku and price > 0:
                # Get expected price range based on product category
                category = sku.split('_')[0] + '_' + sku.split('_')[1] if '_' in sku else 'UNKNOWN'
                expected_range = expected_prices.get(category, (100, 1000))
                
                # Check for price anomalies
                if price < expected_range[0] * 0.5 or price > expected_range[1] * 1.5:
                    anomalies.append({
                        "timestamp": transaction.get('timestamp'),
                        "sku": sku,
                        "actual_price": price,
                        "expected_range": expected_range,
                        "anomaly_type": "PRICE_ANOMALY",
                        "severity": "MEDIUM"
                    })
        except Exception:
            continue
    
    return anomalies

def analyze_manual_recognition(recognition_data):
    """Analyze manually entered product recognition data"""
    if not recognition_data:
        return []
    
    low_confidence_events = []
    
    for event in recognition_data:
        try:
            data = event.get('data', {})
            accuracy = data.get('accuracy', 1.0)
            
            # Flag low confidence recognition (<75% for manual data)
            if accuracy < 0.75:
                severity = "HIGH" if accuracy < 0.5 else "MEDIUM"
                low_confidence_events.append({
                    "timestamp": event.get('timestamp'),
                    "predicted_product": data.get('predicted_product'),
                    "confidence": accuracy,
                    "severity": severity
                })
        except Exception:
            continue
    
    return low_confidence_events

def analyze_manual_queue(queue_data):
    """Analyze manually entered queue data"""
    if not queue_data:
        return []
    
    dwell_anomalies = []
    
    for event in queue_data:
        try:
            data = event.get('data', {})
            avg_dwell_time = data.get('average_dwell_time', 0)
            customer_count = data.get('customer_count', 0)
            
            # Flag suspicious dwell times
            if avg_dwell_time > 180 and customer_count > 0:  # >3 minutes
                severity = "HIGH" if avg_dwell_time > 300 else "MEDIUM"
                dwell_anomalies.append({
                    "timestamp": event.get('timestamp'),
                    "station_id": event.get('station_id', 'UNKNOWN'),
                    "dwell_time": avg_dwell_time,
                    "customer_count": customer_count,
                    "severity": severity
                })
        except Exception:
            continue
    
    return dwell_anomalies

def main():
    """Main manual data analysis function"""
    print("============================================================")
    print("PROJECT SENTINEL - MANUAL DATA ANALYSIS")
    print("============================================================")
    print("🔍 Analyzing manually entered data...")
    
    # Create manual data directory if it doesn't exist
    os.makedirs("data/manual", exist_ok=True)
    
    all_events = []
    analysis_results = {}
    
    # 1. Manual Inventory Analysis
    print("\n1. Analyzing Manual Inventory Data...")
    inventory_data = load_manual_data("inventory_snapshots.jsonl")
    shrinkage_events = analyze_manual_inventory(inventory_data)
    all_events.extend([{**event, "event_type": "INVENTORY_SHRINKAGE"} for event in shrinkage_events])
    analysis_results['inventory'] = {
        "shrinkage_events": shrinkage_events,
        "total_events": len(shrinkage_events)
    }
    print(f"   📊 Found {len(shrinkage_events)} shrinkage events")
    
    # 2. Manual POS Analysis
    print("\n2. Analyzing Manual POS Data...")
    pos_data = load_manual_data("pos_transactions.jsonl")
    pos_anomalies = analyze_manual_pos(pos_data)
    all_events.extend([{**event, "event_type": "POS_ANOMALY"} for event in pos_anomalies])
    analysis_results['pos'] = {
        "anomalies": pos_anomalies,
        "total_events": len(pos_anomalies)
    }
    print(f"   📊 Found {len(pos_anomalies)} POS anomalies")
    
    # 3. Manual Recognition Analysis
    print("\n3. Analyzing Manual Recognition Data...")
    recognition_data = load_manual_data("product_recognition.jsonl")
    low_confidence_events = analyze_manual_recognition(recognition_data)
    all_events.extend([{**event, "event_type": "LOW_CONFIDENCE"} for event in low_confidence_events])
    analysis_results['recognition'] = {
        "low_confidence_events": low_confidence_events,
        "total_events": len(low_confidence_events)
    }
    print(f"   📊 Found {len(low_confidence_events)} low confidence events")
    
    # 4. Manual Queue Analysis
    print("\n4. Analyzing Manual Queue Data...")
    queue_data = load_manual_data("queue_monitoring.jsonl")
    dwell_anomalies = analyze_manual_queue(queue_data)
    all_events.extend([{**event, "event_type": "DWELL_ANOMALY"} for event in dwell_anomalies])
    analysis_results['queue'] = {
        "dwell_anomalies": dwell_anomalies,
        "total_events": len(dwell_anomalies)
    }
    print(f"   📊 Found {len(dwell_anomalies)} dwell anomalies")
    
    # Generate summary
    print("\n============================================================")
    print("MANUAL DATA ANALYSIS COMPLETE")
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
    
    if event_types:
        print(f"\nEvent Types:")
        for event_type, count in event_types.items():
            print(f"  - {event_type}: {count}")
    
    # Generate output files
    os.makedirs("output", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # Save events for submission
    with open("output/manual_events.jsonl", "w") as f:
        for event in all_events:
            f.write(json.dumps(event) + "\n")
    
    # Generate inventory report for dashboard compatibility
    if shrinkage_events:
        # Calculate inventory summary from manual data
        inventory_summary = {
            "initial_inventory": 0,
            "final_inventory": 0,
            "net_change": 0
        }
        
        if inventory_data and len(inventory_data) >= 2:
            first_snapshot = inventory_data[0].get('data', {})
            last_snapshot = inventory_data[-1].get('data', {})
            
            initial_total = sum(first_snapshot.values()) if first_snapshot else 0
            final_total = sum(last_snapshot.values()) if last_snapshot else 0
            
            inventory_summary = {
                "initial_inventory": initial_total,
                "final_inventory": final_total,
                "net_change": final_total - initial_total
            }
        
        # Create report for dashboard
        inventory_report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "data_source": "Manual Data Entry",
            "shrinkage_events": shrinkage_events,
            "summary": inventory_summary
        }
        
        with open("inventory_analysis_report.json", "w") as f:
            json.dump(inventory_report, f, indent=2)
    
    # Save comprehensive manual analysis report
    manual_report = {
        "analysis_timestamp": datetime.now().isoformat(),
        "data_source": "Manual Entry",
        "analysis_type": "Custom Data Analysis",
        "results": analysis_results,
        "summary": {
            "total_events": total_events,
            "high_severity_events": high_severity,
            "medium_severity_events": medium_severity,
            "event_types": event_types
        }
    }
    
    with open("reports/manual_analysis_report.json", "w") as f:
        json.dump(manual_report, f, indent=2)
    
    print(f"\nFiles Generated:")
    print(f"  ✅ output/manual_events.jsonl")
    print(f"  ✅ inventory_analysis_report.json (for dashboard)")
    print(f"  ✅ reports/manual_analysis_report.json")
    
    if total_events > 0:
        print(f"\n🚨 FRAUD DETECTION SUMMARY:")
        print(f"   📊 {total_events} suspicious events detected in manual data")
        print(f"   ⚠️  {high_severity} high-severity alerts require immediate attention")
        print(f"   📈 Analysis shows potential fraud patterns in your data")
    else:
        print(f"\n✅ CLEAN DATA:")
        print(f"   📊 No fraud patterns detected in manual data")
        print(f"   🛡️ Your data appears to be clean and secure")
    
    return 0

if __name__ == "__main__":
    main()
