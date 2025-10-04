#!/usr/bin/env python3
"""
Simple Master Analysis Runner (No Dependencies)
===============================================
"""

import json
import os
from datetime import datetime

def run_simple_analysis():
    """Run simplified analysis of all data sources"""
    
    print("="*60)
    print("PROJECT SENTINEL - SIMPLE FRAUD DETECTION")
    print("="*60)
    
    # Create output directories
    os.makedirs("output", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    all_events = []
    reports = {}
    
    # 1. Inventory Analysis
    print("\n1. Analyzing Inventory Data...")
    try:
        exec(open('simple_inventory_analysis.py').read())
        with open('inventory_simple_report.json', 'r') as f:
            inventory_report = json.load(f)
        reports['inventory'] = inventory_report
        
        # Convert shrinkage events to standard format
        for event in inventory_report.get('shrinkage_events', []):
            all_events.append({
                'timestamp': event['timestamp'],
                'event_type': 'INVENTORY_SHRINKAGE',
                'location': 'STORE_FLOOR',
                'severity': event['severity'].lower(),
                'confidence': 0.8,
                'description': f"Inventory decrease of {event['decrease_percentage']:.1f}% for {event['product']}",
                'metadata': {
                    'product_sku': event['product'],
                    'quantity_change': event['current_qty'] - event['previous_qty'],
                    'percentage_decrease': event['decrease_percentage']
                }
            })
        
        print(f"   ✓ Found {len(inventory_report.get('shrinkage_events', []))} shrinkage events")
        
    except Exception as e:
        print(f"   ✗ Inventory analysis failed: {e}")
    
    # 2. POS Analysis
    print("\n2. Analyzing POS Transaction Data...")
    try:
        exec(open('simple_pos_analysis.py').read())
        with open('pos_simple_report.json', 'r') as f:
            pos_report = json.load(f)
        reports['pos'] = pos_report
        
        # Convert weight discrepancies to standard format
        for event in pos_report.get('weight_discrepancies', []):
            all_events.append({
                'timestamp': event['timestamp'],
                'event_type': 'WEIGHT_DISCREPANCY',
                'location': event['station_id'],
                'severity': event['severity'].lower(),
                'confidence': 0.85,
                'description': f"Weight discrepancy of {event['weight_difference_pct']:.1f}% for {event['product_name']}",
                'metadata': {
                    'customer_id': event['customer_id'],
                    'expected_weight': event['expected_weight'],
                    'actual_weight': event['actual_weight']
                }
            })
        
        print(f"   ✓ Found {len(pos_report.get('weight_discrepancies', []))} weight discrepancies")
        
    except Exception as e:
        print(f"   ✗ POS analysis failed: {e}")
    
    # 3. Simple Product Recognition Analysis
    print("\n3. Analyzing Product Recognition Data...")
    try:
        recognition_data = []
        with open('data/input/product_recognition.jsonl', 'r') as f:
            for line in f:
                record = json.loads(line.strip())
                recognition_data.append(record)
        
        low_confidence_events = []
        for record in recognition_data:
            if record['data']['accuracy'] < 0.7:
                low_confidence_events.append({
                    'timestamp': record['timestamp'],
                    'station_id': record['station_id'],
                    'predicted_product': record['data']['predicted_product'],
                    'confidence': record['data']['accuracy'],
                    'severity': 'HIGH' if record['data']['accuracy'] < 0.5 else 'MEDIUM'
                })
                
                if record['data']['accuracy'] < 0.5:  # Only very low confidence
                    all_events.append({
                        'timestamp': record['timestamp'],
                        'event_type': 'SCANNER_AVOIDANCE',
                        'location': record['station_id'],
                        'severity': 'medium',
                        'confidence': 0.6,
                        'description': f"Very low product recognition confidence ({record['data']['accuracy']:.2f})",
                        'metadata': {
                            'predicted_product': record['data']['predicted_product'],
                            'recognition_confidence': record['data']['accuracy']
                        }
                    })
        
        reports['recognition'] = {
            'low_confidence_events': low_confidence_events,
            'summary': {
                'total_events': len(recognition_data),
                'low_confidence_count': len(low_confidence_events),
                'avg_confidence': sum(r['data']['accuracy'] for r in recognition_data) / len(recognition_data)
            }
        }
        
        print(f"   ✓ Found {len(low_confidence_events)} low confidence events")
        
    except Exception as e:
        print(f"   ✗ Recognition analysis failed: {e}")
    
    # 4. Simple Queue Analysis
    print("\n4. Analyzing Queue Data...")
    try:
        queue_data = []
        with open('data/input/queue_monitoring.jsonl', 'r') as f:
            for line in f:
                record = json.loads(line.strip())
                queue_data.append(record)
        
        dwell_anomalies = []
        for record in queue_data:
            if record['data']['customer_count'] > 0:
                dwell_time = record['data']['average_dwell_time']
                
                if dwell_time > 300:  # 5+ minutes
                    dwell_anomalies.append({
                        'timestamp': record['timestamp'],
                        'station_id': record['station_id'],
                        'dwell_time': dwell_time,
                        'customer_count': record['data']['customer_count'],
                        'severity': 'HIGH' if dwell_time > 600 else 'MEDIUM'
                    })
                    
                    if dwell_time > 600:  # Only very long dwell times
                        all_events.append({
                            'timestamp': record['timestamp'],
                            'event_type': 'CHECKOUT_DIFFICULTY',
                            'location': record['station_id'],
                            'severity': 'medium',
                            'confidence': 0.5,
                            'description': f"Unusually long dwell time: {dwell_time:.1f}s",
                            'metadata': {
                                'dwell_time': dwell_time,
                                'customer_count': record['data']['customer_count']
                            }
                        })
        
        reports['queue'] = {
            'dwell_anomalies': dwell_anomalies,
            'summary': {
                'total_observations': len(queue_data),
                'dwell_anomalies_count': len(dwell_anomalies)
            }
        }
        
        print(f"   ✓ Found {len(dwell_anomalies)} dwell time anomalies")
        
    except Exception as e:
        print(f"   ✗ Queue analysis failed: {e}")
    
    # 5. Simple RFID Analysis  
    print("\n5. Analyzing RFID Data...")
    try:
        rfid_data = []
        with open('data/input/rfid_readings.jsonl', 'r') as f:
            for line in f:
                record = json.loads(line.strip())
                rfid_data.append(record)
        
        null_readings = len([r for r in rfid_data if r['data']['epc'] is None])
        total_readings = len(rfid_data)
        detection_rate = (total_readings - null_readings) / total_readings if total_readings > 0 else 0
        
        reports['rfid'] = {
            'summary': {
                'total_readings': total_readings,
                'detection_rate': detection_rate,
                'null_readings': null_readings
            }
        }
        
        print(f"   ✓ RFID detection rate: {detection_rate:.1%}")
        
    except Exception as e:
        print(f"   ✗ RFID analysis failed: {e}")
    
    # Sort events by timestamp
    all_events.sort(key=lambda x: x['timestamp'])
    
    # Save events.jsonl for submission
    with open("output/events.jsonl", "w") as f:
        for event in all_events:
            f.write(json.dumps(event) + "\n")
    
    # Generate master report
    master_report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'project': 'Project Sentinel - Simple Fraud Detection',
        'reports': reports,
        'events_detected': all_events,
        'summary': {
            'total_events': len(all_events),
            'high_severity_events': len([e for e in all_events if e['severity'] == 'high']),
            'medium_severity_events': len([e for e in all_events if e['severity'] == 'medium']),
            'event_types': list(set(e['event_type'] for e in all_events)),
            'locations_affected': list(set(e['location'] for e in all_events if e['location'] != 'STORE_FLOOR'))
        }
    }
    
    with open("reports/master_simple_report.json", "w") as f:
        json.dump(master_report, f, indent=2)
    
    # Print final summary
    print("\n" + "="*60)
    print("FRAUD DETECTION ANALYSIS COMPLETE")
    print("="*60)
    print(f"Total Events Detected: {len(all_events)}")
    print(f"High Severity Events: {len([e for e in all_events if e['severity'] == 'high'])}")
    print(f"Medium Severity Events: {len([e for e in all_events if e['severity'] == 'medium'])}")
    
    event_counts = {}
    for event in all_events:
        event_type = event['event_type']
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
    
    print(f"\nEvent Types:")
    for event_type, count in event_counts.items():
        print(f"  - {event_type}: {count}")
    
    print(f"\nFiles Generated:")
    print(f"  - output/events.jsonl (for submission)")
    print(f"  - reports/master_simple_report.json (detailed report)")
    
    return master_report

if __name__ == "__main__":
    report = run_simple_analysis()
